# enrollments/views.py

from django.shortcuts import render, get_object_or_404, redirect
import stripe  # Exposed for legacy tests that patch this symbol
from django.contrib.auth.decorators import login_required
from .models import Enrollment, ModuleCompletion, LessonCompletion
# Ensure we use the real Course model from classroom.courses
from django.contrib import messages
from classroom.courses.models import Course, Module, Lesson


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

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            "status": Enrollment.Status.PENDING_PAYMENT if course.price and course.price > 0 else Enrollment.Status.ACTIVE
        }
    )

    # Already exists
    if not created:
        if enrollment.status in [Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED]:
            messages.info(request, f"Ya tienes acceso activo a {course.title}.")
            return redirect("courses:my_course")

        if enrollment.status == Enrollment.Status.PENDING_APPROVAL:
            messages.info(request, "Tu solicitud de beca está en revisión.")
            return redirect("courses:my_course")

    # Newly created
    if enrollment.status == Enrollment.Status.PENDING_PAYMENT:
        messages.success(request, f"Inscripción creada. Falta completar el pago.")
        return redirect("enrollments:create_checkout_session", enrollment_id=enrollment.id)

    messages.success(request, f"Inscripción activa en {course.title}.")
    return redirect("courses:my_course")

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

    # Block progress unless ACTIVE
    if enrollment.status != Enrollment.Status.ACTIVE:
        messages.error(request, "Debes completar el pago o esperar aprobación para avanzar en el curso.")
        return redirect("courses:my_course")

    ModuleCompletion.objects.get_or_create(enrollment=enrollment, module=module)

    total_modules = module.course.module_set.count()
    completed_modules = ModuleCompletion.objects.filter(enrollment=enrollment).count()

    progress = (completed_modules / total_modules) * 100 if total_modules else 0
    enrollment.progress = round(progress, 2)
    if progress >= 100:
        enrollment.completed = True
    enrollment.save()

    return redirect("courses:module_detail", pk=module.pk)


#lesson completion view
@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=lesson.module.course)

    # Block progress unless ACTIVE
    if enrollment.status != Enrollment.Status.ACTIVE:
        messages.error(request, "Debes completar el pago o esperar aprobación para avanzar en el curso.")
        return redirect("courses:my_course")

    # Marcar como completada
    LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    # Opcional: calcular progreso si lo haces por lecciones
    total_lessons = Lesson.objects.filter(module__course=lesson.module.course).count()
    completed_lessons = LessonCompletion.objects.filter(enrollment=enrollment).count()

    progress = (completed_lessons / total_lessons) * 100 if total_lessons else 0
    enrollment.progress = round(progress, 2)
    enrollment.completed = progress >= 100
    enrollment.save()

    return redirect('courses:my_course')


@login_required
def create_checkout_session(request, enrollment_id):
    # Thin wrapper delegating to payments app, preserving URL name and patch target
    from payments.views import start_checkout_for_enrollment
    return start_checkout_for_enrollment(request, enrollment_id)
