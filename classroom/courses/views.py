from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course, Module, Lesson
from .forms import CourseForm, ModuleForm, LessonForm
from django.contrib import messages

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Module, TestResult
from classroom.enrollments.models import Enrollment


# 🔹 Listar cursos publicados
def course_list(request):
    can_access_module = request.user.has_perm('groups.access_module')
    courses = Course.objects.filter(published=True)
    context = {
        'courses': courses,
        'can_access_module': can_access_module,
    }
    return render(request, 'courses/course_list.html', context)

# 🔹 Detalle de curso
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()

    context = {
        'object': course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)

# 🔹 Crear curso
@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('courses:course-list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

# 🔹 Actualizar curso
@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:course-list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'object': course})

# 🔹 Eliminar curso
@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('courses:course-list')
    context = {
        'courses': course
    }
    return render(request, 'courses/course_confirm_delete.html', context)

# modules funciones
@login_required
def module_create(request):
    form = ModuleForm()
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = get_object_or_404(Course, pk=request.POST.get('course_id'))
            module.save()
            messages.success(request, 'Module created successfully.')
            return redirect('module_create') #return redirect('courses:course-detail', pk=module.course.pk)
        else:
            messages.error(request, 'Error creating module. Please correct the errors below.')
            return redirect('courses:module-create')
    else:
        form = ModuleForm()
    context = {
        'form': form,
        'courses': Course.objects.all()
    }
    return render(request, 'module/module_form.html', context)

@login_required
def module_list(request):
    modules = Module.objects.all()
    context = {
        'modules': modules,
    }
    return render(request, 'modules/module_list.html', context)

@login_required
def module_update(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('module:module-detail', pk=module.course.pk)
    else:
        form = ModuleForm(instance=module)
    context = {
        'form': form,
    }
    return render(request, 'modules/module_form.html', context)

@login_required
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    lessons = module.lessons.all()
    context = {
        'module': module,
        'lessons': lessons,
    }
    return render(request, 'modules/module_detail.html', context)

@login_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('courses:module-list')
    else:
        messages.error(request, 'Error deleting module.')
        return redirect('courses:module-list')
        
    context = {
        'module': module
    }
    return render(request, 'courses/module_confirm_delete.html', context)


# 🔹 Lecciones funciones
@login_required
def lesson_list(request):
    lessons = Lesson.objects.all()
    context = {
        'lessons': lessons,
    }
    return render(request, 'lessons/lesson_list.html', context)

@login_required
def lesson_create(request):
    form = LessonForm()
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = get_object_or_404(Module, pk=request.POST.get('module_id'))
            lesson.save()
            messages.success(request, 'Lesson created successfully.')
            return redirect('courses:module-detail', pk=lesson.module.pk)
    context = {
        'form': form,
        'modules': Module.objects.all()
    }
    return render(request, 'lessons/lesson_form.html', context)

@login_required
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully.')
            return redirect('courses:module-detail', pk=lesson.module.pk)
    else:
        form = LessonForm(instance=lesson)
    context = {
        'form': form,
    }
    return render(request, 'lessons/lesson_form.html', context)

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    context = {
        'lesson': lesson,
    }
    return render(request, 'lessons/lesson_detail.html', context)

@login_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully.')
        return redirect('courses:lesson-list')
    else:
        messages.error(request, 'Error deleting lesson.')
        return redirect('courses:lesson-list')
    context = {
        'lesson': lesson
    }
    return render(request, 'lessons/lesson_confirm_delete.html', context)

# guarda los resultados del test
@csrf_exempt
@login_required
def save_test_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        module_id = data.get('module_id')
        score = data.get('score')

        module = Module.objects.get(pk=module_id)
        test = module.test
        user = request.user

        # Busca enrollment
        enrollment = Enrollment.objects.get(user=user, course=module.course)

        # Guarda resultado
        result, created = TestResult.objects.get_or_create(
            enrollment=enrollment,
            test=test,
            defaults={'score': score}
        )
        if not created:
            result.score = score
            result.save()

        # BONUS: marcar módulo como completado si score >= 70%
        if score >= 70:
            enrollment.progress += 10  # Ejemplo de progreso, ajusta a tu lógica
            enrollment.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def test_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    test = module.test
    if request.method == 'POST':
        data = json.loads(request.body)
        score = data.get('score')
        # Aquí podrías guardar el resultado del test si es necesario
        return JsonResponse({'status': 'success', 'score': score})
    
    return render(request, 'courses/test_detail.html', {'module': module, 'test': test})


@login_required
def course_enroll(request, pk):
    course = get_object_or_404(Course, pk=pk)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return redirect('courses:course-detail', pk=pk)