# enrollments/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Enrollment, ModuleCompletion, LessonCompletion, Payment
# Ensure we use the real Course model from classroom.courses
from django.urls import reverse
from django.contrib import messages
from classroom.courses.models import Course, Module, Lesson
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import stripe

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

@login_required
def enrollment_list(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'enrollments_list.html', {'enrollments': enrollments})

@login_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
    return render(request, 'enrollment_detail.html', {'enrollment': enrollment})

@login_required
def enrollment_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        messages.success(request, f"Te has inscrito en {course.title}.")
    else:
        messages.info(request, f"Ya estás inscrito en {course.title}.")
    return redirect('enrollments:enrollment-list')

@login_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, "Inscripción eliminada.")
        return redirect('enrollments:enrollment-list')
    return render(request, 'enrollment_confirm_delete.html', {'enrollment': enrollment})

#module completion view
@login_required
def mark_module_complete(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=module.course)

    # Registrar el módulo como completado
    ModuleCompletion.objects.get_or_create(enrollment=enrollment, module=module)

    # Calcular el progreso
    total_modules = module.course.module_set.count()
    completed_modules = ModuleCompletion.objects.filter(enrollment=enrollment).count()

    progress = (completed_modules / total_modules) * 100
    enrollment.progress = progress
    if progress >= 100:
        enrollment.completed = True
    enrollment.save()

    return redirect('courses:module_detail', pk=module.pk)

#lesson completion view
@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=lesson.module.course)

    # Marcar como completada
    LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    # Opcional: calcular progreso si lo haces por lecciones
    total_lessons = Lesson.objects.filter(module__course=lesson.module.course).count()
    completed_lessons = LessonCompletion.objects.filter(enrollment=enrollment).count()

    progress = (completed_lessons / total_lessons) * 100
    enrollment.progress = round(progress, 2)
    enrollment.completed = progress >= 100
    enrollment.save()

    return redirect('courses:my_course')


@login_required
def create_checkout_session(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id, user=request.user)
    course = enrollment.course
    if enrollment.status != Enrollment.Status.PENDING_PAYMENT:
        messages.info(request, 'Esta matrícula no requiere pago.')
        return redirect('courses:my_course')

    amount = course.price or 0
    payment = Payment.objects.create(
        user=request.user,
        course=course,
        enrollment=enrollment,
        amount=amount,
        status='created'
    )

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': course.title},
                    'unit_amount': int(float(amount) * 100),
                },
                'quantity': 1,
            }],
            metadata={'enrollment_id': str(enrollment.id), 'user_id': str(request.user.id)},
            client_reference_id=str(enrollment.id),
            success_url=f"{request.build_absolute_uri('/')[:-1]}/classroom/enrollments/payment/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.build_absolute_uri('/')[:-1]}/classroom/enrollments/payment/cancel/",
        )
        payment.stripe_session_id = session.id
        payment.save()
        return redirect(session.url, permanent=False)
    except Exception:
        messages.error(request, 'No se pudo iniciar el pago. Intenta más tarde.')
        return redirect('courses:my_course')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    # Idempotency via StripeEvent
    event_id = event.get('id')
    event_type = event.get('type')
    from .models import StripeEvent
    if event_id and StripeEvent.objects.filter(event_id=event_id).exists():
        return HttpResponse(status=200)
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        payment = Payment.objects.filter(stripe_session_id=session.get('id')).select_related('enrollment', 'course', 'user').first()
        # Validate metadata ownership
        meta = session.get('metadata', {}) or {}
        enrollment_id_meta = meta.get('enrollment_id')
        user_id_meta = meta.get('user_id')
        if payment:
            if enrollment_id_meta and str(payment.enrollment.id) != str(enrollment_id_meta):
                return HttpResponse(status=200)
            if user_id_meta and str(payment.user.id) != str(user_id_meta):
                return HttpResponse(status=200)
            # Idempotency guard: if already paid, skip
            if payment.status == 'paid':
                return HttpResponse(status=200)
            payment.status = 'paid'
            payment.save()
            enrollment = payment.enrollment
            # Only update if not already active/completed
            if enrollment.status in (Enrollment.Status.PENDING_PAYMENT, Enrollment.Status.PENDING_APPROVAL, Enrollment.Status.REJECTED, Enrollment.Status.ACTIVE):
                enrollment.status = Enrollment.Status.ACTIVE
                enrollment.save()
            # Email confirmación de pago
            try:
                if payment.user.email:
                    from django.core.mail import EmailMessage
                    EmailMessage(
                        subject='Pago confirmado',
                        body=f'Tu pago del curso {enrollment.course.title} fue confirmado. Ya tienes acceso activo.',
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                        to=[payment.user.email],
                    ).send(fail_silently=True)
            except Exception:
                pass
            # Persist processed event id
            if event_id:
                try:
                    StripeEvent.objects.create(event_id=event_id, type=event_type)
                except Exception:
                    pass
    return HttpResponse(status=200)
