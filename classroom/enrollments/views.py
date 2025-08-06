# enrollments/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Enrollment, ModuleCompletion, LessonCompletion
#from courses.models import Course
from django.urls import reverse
from django.contrib import messages
from classroom.courses.models import Course, Module, Lesson

@login_required
def enrollment_list(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'enrollments/enrollment_list.html', {'enrollments': enrollments})

@login_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
    return render(request, 'enrollments/enrollment_detail.html', {'enrollment': enrollment})

@login_required
def enrollment_create(request, course_id):
    Course = "test"
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
    return render(request, 'enrollments/enrollment_confirm_delete.html', {'enrollment': enrollment})

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
