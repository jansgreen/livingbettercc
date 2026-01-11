# enrollments/views.py

from django.shortcuts import render, get_object_or_404, redirect
import stripe  # Exposed for legacy tests that patch this symbol
# Ensure we use the real Course model from classroom.courses
from classroom.courses.models import Course, Module, Lesson
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from classroom.enrollments.models import Enrollment, ModuleCompletion, LessonCompletion
from classroom.courses.models import Module
from classroom.quicktest.models import QuickTest, QuickTestDefinition

PASSING_SCORE = 70

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


@login_required
def mark_module_complete(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    course = module.course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    if enrollment.status != Enrollment.Status.ACTIVE:
        messages.error(request, "Debes completar el pago o esperar aprobación para avanzar en el curso.")
        return redirect("courses:my_course")

    # Si el módulo tiene QuickTest, exigir aprobado antes de marcar módulo completado
    if QuickTestDefinition.objects.filter(module=module).exists():
        qt = (
            QuickTest.objects
            .filter(user=request.user, module=module)
            .order_by("-completed_at")
            .first()
        )
        if (not qt) or (float(qt.score) < PASSING_SCORE):
            messages.info(request, "Debes aprobar el test de este módulo antes de marcarlo como completado.")
            return redirect("courses:module_detail", pk=module.pk)

    ModuleCompletion.objects.get_or_create(enrollment=enrollment, module=module)

    total_modules = course.modules.count()
    completed_modules = ModuleCompletion.objects.filter(enrollment=enrollment).count()

    progress = (completed_modules / total_modules) * 100 if total_modules else 0
    enrollment.progress = round(progress, 2)

    # NO completar curso aquí
    enrollment.save(update_fields=["progress"])

    messages.success(request, "Módulo marcado como completado.")
    return redirect("courses:module_detail", pk=module.pk)

@login_required
def create_checkout_session(request, enrollment_id):
    # Thin wrapper delegating to payments app, preserving URL name and patch target
    from payments.views import start_checkout_for_enrollment
    return start_checkout_for_enrollment(request, enrollment_id)

@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    module = lesson.module
    course = module.course

    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    # Bloquear progreso si no está ACTIVE
    if enrollment.status != Enrollment.Status.ACTIVE:
        messages.error(request, "Debes completar el pago o esperar aprobación para avanzar en el curso.")
        return redirect("courses:my_course")

    # Enforce orden dentro del módulo
    ordered_lessons = list(module.lessons.order_by("order", "id"))

    try:
        idx = next(i for i, l in enumerate(ordered_lessons) if l.id == lesson.id)
    except StopIteration:
        messages.error(request, "Lección inválida para este módulo.")
        return redirect("courses:my_course")

    prev_lessons = ordered_lessons[:idx]
    prev_ids = [l.id for l in prev_lessons]

    if prev_ids:
        completed_prev_ids = set(
            LessonCompletion.objects.filter(
                enrollment=enrollment,
                lesson_id__in=prev_ids
            ).values_list("lesson_id", flat=True)
        )

        if len(completed_prev_ids) < len(prev_ids):
            first_pending = next((l for l in prev_lessons if l.id not in completed_prev_ids), None)
            messages.warning(request, "Debes completar las lecciones en orden.")
            if first_pending:
                return redirect("courses:lesson_detail", pk=first_pending.id)
            return redirect("courses:my_course")

    # Marcar lección completada (idempotente)
    LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    # Progreso del curso basado en lecciones (NO finaliza aquí)
    total_lessons = Lesson.objects.filter(module__course=course).count()
    completed_lessons = LessonCompletion.objects.filter(enrollment=enrollment).count()

    progress = (completed_lessons / total_lessons) * 100 if total_lessons else 0
    enrollment.progress = round(progress, 2)
    enrollment.save(update_fields=["progress"])

    messages.success(request, "Lección marcada como completada.")
    return redirect("courses:my_course")
