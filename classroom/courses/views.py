from .models import Module, Question, QuickTestResult
from classroom.certifications.views import create_certificate_for_user

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Lesson
from .forms import CourseForm, ModuleForm, LessonForm
from classroom.enrollments.models import Enrollment, LessonCompletion
from django.contrib import messages

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from .models import Course
from authentication.models.students import Students  # Ajusta el import según tu estructura
from authentication.models.profiles import Profiles

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import Group
from classroom.courses.models import Course, Module, Lesson


@login_required
def quicktest_view(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    test = getattr(module, 'test', None)
    if not test:
        messages.error(request, 'Este módulo no tiene test asignado.')
        return redirect('courses:module_detail', pk=module_id)

    if request.method == 'POST':
        correct = 0
        total = test.questions.count()
        for q in test.questions.all():
            user_answer = request.POST.get(f'question_{q.id}')
            if user_answer == q.correct_option:
                correct += 1
        score = (correct / total) * 100 if total > 0 else 0
        passed = score >= 70
        QuickTestResult.objects.update_or_create(
            user=request.user,
            module=module,
            defaults={'score': score, 'passed': passed}
        )
        if passed:
            messages.success(request, '¡Test aprobado! Puedes continuar al siguiente módulo.')
            return redirect('courses:next_module', module_id=module_id)
        else:
            messages.error(request, 'No aprobaste el test. Repasa la lección antes de continuar.')
            return redirect('courses:module_detail', pk=module_id)

    return render(request, 'courses/quicktest.html', {'module': module, 'test': test})

def course_enroll(request, pk):
    """Permite a un usuario inscribirse en un curso."""
    if not request.user.is_authenticated:
        # Guardar intención en sesión para redirigir al curso después del registro
        request.session['post_register_role'] = 'student'
        request.session['selected_item'] = pk
        # Si viene un POST con datos de beca, guardarlos temporalmente en sesión
        if request.method == 'POST' and 'cedula' in request.POST:
            pending = {
                'cedula': request.POST.get('cedula', '').strip(),
                'exequatur': request.POST.get('exequatur', '').strip(),
                'centro_educativo': request.POST.get('centro_educativo', '').strip(),
                'distrito_escolar': request.POST.get('distrito_escolar', '').strip(),
                'street': request.POST.get('street', '').strip(),
                'neighborhood': request.POST.get('neighborhood', '').strip(),
                'provincia': request.POST.get('provincia', '').strip(),
                'municipio': request.POST.get('municipio', '').strip(),
                'zip_code': request.POST.get('zip_code', '').strip(),
                'city': request.POST.get('city', '').strip(),
                'state': request.POST.get('state', '').strip(),
            }
            request.session['pending_beca'] = pending
        messages.warning(request, 'Debes iniciar sesión o registrarte para inscribirte en un curso.')
        return redirect('register')

    user = request.user
    course = get_object_or_404(Course, pk=pk)

    # Crear o recuperar estudiante
    student, created = Students.objects.get_or_create(user=user)

    # Asegurarse de que el usuario pertenezca al grupo 'student'
    student_group, _ = Group.objects.get_or_create(name='student')
    if not user.groups.filter(name='student').exists():
        user.groups.add(student_group)

    # Verificar si el usuario tiene perfil
    profile = Profiles.objects.filter(user=user).first()
    if not profile:
        messages.info(request, 'Por favor, crea tu perfil antes de inscribirte.')
        return redirect('profile_create')

    # Si el usuario aplica a beca Minerd (POST con cedula y exequatur)
    if request.method == 'POST' and 'cedula' in request.POST and 'exequatur' in request.POST:
        cedula = request.POST.get('cedula', '').strip()
        exequatur = request.POST.get('exequatur', '').strip()
        centro_educativo = request.POST.get('centro_educativo', '').strip()
        distrito_escolar = request.POST.get('distrito_escolar', '').strip()
        # Dirección laboral
        street = request.POST.get('street', '').strip()
        neighborhood = request.POST.get('neighborhood', '').strip()
        provincia = request.POST.get('provincia', '').strip()
        municipio = request.POST.get('municipio', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        # Validar profesional
        if not profile.profesion:
            messages.error(request, 'Debes tener una profesión registrada en tu perfil para aplicar a la beca Minerd.')
            return redirect('courses:course_detail', pk=pk)
        if not cedula or not exequatur or not centro_educativo or not distrito_escolar:
            messages.error(request, 'Debes completar todos los campos para aplicar a la beca Minerd.')
            return redirect('courses:course_detail', pk=pk)
        # Guardar datos en Students
        student.cedula = cedula
        student.certification = exequatur
        student.save()
        # Guardar dirección laboral
        from authentication.models.address import Address
        address = Address.objects.create(
            user=user,
            address_type='laboral',
            street=street,
            neighborhood=neighborhood,
            city=city,
            state=state,
            zip_code=zip_code
        )
        # Guardar aplicación a beca
        from classroom.enrollments.models import BecaApplication
        BecaApplication.objects.create(
            user=user,
            course=course,
            cedula=cedula,
            exequatur=exequatur,
            centro_educativo=centro_educativo,
            distrito_escolar=distrito_escolar,
            address=address
        )
        # Crear o recuperar matrícula
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        if created:
            messages.success(request, f'Tu aplicación a la beca Minerd para {course.title} fue enviada correctamente.')
        else:
            messages.info(request, f'Ya tienes una aplicación/matrícula para este curso.')
        return redirect('courses:my_course')

    # Inscripción normal (pago)
    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
    if created:
        messages.success(request, f'Te has matriculado con éxito en {course.title}.')
    else:
        messages.info(request, f'Ya estás matriculado en {course.title}.')

    return redirect('courses:my_course')

def course_list(request):
    can_access_module = request.user.has_perm('groups.access_module')
    courses = Course.objects.filter(published=True)
    context = {
        'courses': courses,
        'can_access_module': can_access_module,
    }
    return render(request, 'courses/course_list.html', context)

def course_detail(request, pk):
    course = Course.objects.prefetch_related('modules__lessons').get(pk=pk)

    is_enrolled = False
    beca_status = None
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).first()
        # Consultar estado de beca Minerd para este curso
        from classroom.enrollments.models import BecaApplication
        beca_app = BecaApplication.objects.filter(user=request.user, course=course).order_by('-fecha_aplicacion').first()
        if beca_app:
            beca_status = beca_app.estado
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'beca_status': beca_status,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def my_course(request):
    enrollments = Enrollment.objects.filter(user=request.user, completed=False)
    courses = Course.objects.filter(enrollment__in=enrollments).distinct()
    modules = Module.objects.filter(course__in=courses).distinct()
    course_ids = courses.values_list('id', flat=True)

    completed_ids = LessonCompletion.objects.filter(
        enrollment__in=enrollments,
        lesson__module__course__in=course_ids
    ).values_list('lesson_id', flat=True)

    context = {
        'enrollments': enrollments,
        'courses': courses,
        'modules': modules,
        'is_completed': completed_ids,

    }
    return render(request, 'courses/my_course.html', context)

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('courses:course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('courses:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'object': course})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('courses:course_list')
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
            course_id = request.POST.get('course')
            module.course = get_object_or_404(Course, pk=course_id)
            module.save()
            messages.success(request, 'Module created successfully.')
            return redirect('courses:module_create') #return redirect('courses:course-detail', pk=module.course.pk)
        else:
            messages.error(request, 'Error creating module. Please correct the errors below.')
            return redirect('courses:module_create')
    context = {
        'form': form,
        'courses': Course.objects.all()
    }
    return render(request, 'module/module_form.html', context)

@login_required
def module_list(request):
    modules = Module.objects.all()
    lessons = Lesson.objects.filter(module__in=modules)
    context = {
        'modules': modules,
        'lessons': lessons,
    }
    return render(request, 'module/module_list.html', context)

@login_required
def module_update(request, pk):
    module = get_object_or_404(Module, pk=pk)
    form = ModuleForm(instance=module)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully.')
            return redirect('courses:module_list')
        else:
            messages.error(request, 'Error updating module. Please correct the errors below.')
            return redirect('courses:module_update', pk=pk)
    context = {
        'form': form,
        'courses': Course.objects.all(),
        'module': module,
        'object': True,
    }
    return render(request, 'module/module_form.html', context)

@login_required
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    lessons = module.lessons.all()
    quicktest_result = None
    if request.user.is_authenticated and module.test:
        from .models import QuickTestResult
        quicktest_result = QuickTestResult.objects.filter(user=request.user, module=module).first()
    context = {
        'module': module,
        'lessons': lessons,
        'quicktest_result': quicktest_result,
    }
    return render(request, 'module/module_detail.html', context)

@login_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('courses:module_list')
    context = {
        'module': module,
    }
    return render(request, 'module/module_confirm_delete.html', context)

# 🔹 Lecciones funciones
@login_required
def lesson_list(request):
    lessons = Lesson.objects.all()
    context = {
        'lessons': lessons,
    }
    return render(request, 'lesson/lesson_list.html', context)

@login_required
def lesson_create(request):
    form = LessonForm()
    print(request.POST)
    if request.method == 'POST':
        form = LessonForm(request.POST)

        if form.is_valid():
            lesson = form.save(commit=False)
            module_id = request.POST.get('module')
            lesson.module = get_object_or_404(Module, pk=module_id)
            lesson.save()

            messages.success(request, 'Lesson created successfully.')
            return redirect('courses:module_list')
        else:
            messages.error(request, 'Error creating lesson. Please correct the errors below.')
            return redirect('courses:lesson_create')
    context = {
        'form': form,
        'courses': Course.objects.all(),
        'object': False,  # Indica que no es una edición
    }
    return render(request, 'lesson/lesson_form.html', context)

@login_required
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST': #A
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully.')
            return redirect('courses:module_list')
    else:
        form = LessonForm(instance=lesson)
    context = {
        'form': form,
        'lesson': lesson,
        'object': True,
    }
    return render(request, 'lesson/lesson_form.html', context)

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    context = {
        'lessons': lesson,
    }
    return render(request, 'lesson/lesson_detail.html', context)

@login_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully.')
        return redirect('courses:module_list')
    else:
        messages.error(request, 'Error deleting lesson.')
        return redirect('courses:module_list')


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
        result, created = QuickTestResult.objects.get_or_create(
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
def next_module(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    course = module.course
    next_mod = Module.objects.filter(course=course, order__gt=module.order).order_by('order').first()
    if next_mod:
        quicktests = Question.objects.filter(module=next_mod, user=request.user)
        if quicktests.exists():
            messages.info(request, 'Debes completar el test del módulo anterior antes de continuar.')
            return redirect('courses:quicktest_detail', pk=quicktests.first().pk)
        return redirect('courses:module_detail', pk=next_mod.pk)
    else:
        # El usuario ha completado todos los módulos del curso
        # Marcar la matrícula como completada
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment:
            enrollment.completed = True
            enrollment.save()
        create_certificate_for_user(request.user, course)
        messages.success(request, '¡Has completado todos los módulos de este curso! Se ha generado tu certificado.')
        return redirect('courses:my_course')





