from django.urls import reverse
from classroom.courses.models import Course, Module, Lesson
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from classroom.enrollments.models import Enrollment, LessonCompletion, ModuleCompletion


def obtener_menu_classroom(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Classroom',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            #courses/
            menu[0]['submenus'].append({'nombre': 'Crear Curso', 'url': reverse('courses:course_create')})
            menu[0]['submenus'].append({'nombre': 'Lista de Cursos', 'url': reverse('courses:course_list')})
            # Modules
            menu[0]['submenus'].append({'nombre': 'Crear Modulo', 'url': reverse('courses:module_create')})
            menu[0]['submenus'].append({'nombre': 'Modulos', 'url': reverse('courses:module_list')})
            # Lessons
            menu[0]['submenus'].append({'nombre': 'Lecciones', 'url': reverse('courses:lesson_list')})
            menu[0]['submenus'].append({'nombre': 'Crear Lección', 'url': reverse('courses:lesson_create')})

        return {'menu_classroom': menu}
    else:
        return {'menu_classroom': None}

def obtener_progress_class(request):
    if not request.user.is_authenticated:
        return {'progress_classroom': None}

    # Solo cursos en los que el usuario está inscrito y publicados
    enrollments = Enrollment.objects.filter(
        user=request.user,
        course__published=True
    ).select_related('course')

    # Obtener lecciones y módulos completados por el usuario
    lesson_completions = LessonCompletion.objects.filter(enrollment__user=request.user)
    module_completions = ModuleCompletion.objects.filter(enrollment__user=request.user)

    completed_lessons = {lc.lesson_id for lc in lesson_completions}
    completed_modules = {mc.module_id for mc in module_completions}

    progress = []

    for enrollment in enrollments:

        if enrollment.completed:
            continue
        
        course = enrollment.course
        course_modules = course.modules.prefetch_related('lessons')

        total_lessons = 0
        completed_lessons_count = 0
        modules_progress = []

        for module in course_modules:
            module_lessons = module.lessons.all()
            module_total = module_lessons.count()
            module_completed = sum(1 for lesson in module_lessons if lesson.id in completed_lessons)

            total_lessons += module_total
            completed_lessons_count += module_completed

            modules_progress.append({
                'module': module,
                'lessons': [
                    {
                        'lesson': lesson,
                        'completed': lesson.id in completed_lessons
                    }
                    for lesson in module_lessons
                ],
                'module_completed': module.id in completed_modules
            })

        course_progress = 0
        if total_lessons > 0:
            course_progress = round((completed_lessons_count / total_lessons) * 100, 2)

        progress.append({
            'course': course,
            'enrollment': enrollment,
            'progress': course_progress,
            'modules': modules_progress,
            'completed': enrollment.completed,
        })

    return {'progress_classroom': progress}

def obtener_certificados_usuario(request):
    if not request.user.is_authenticated:
        return {'certificados_usuario': []}

    user = request.user
    enrollments = Enrollment.objects.filter(
        user=user,
        course__published=True
    ).select_related('course')

    certificados = []

    for enrollment in enrollments:
        curso = enrollment.course
        total_lessons = 0
        completed_lessons = 0

        for modulo in curso.modules.prefetch_related('lessons'):
            for leccion in modulo.lessons.all():
                completada = LessonCompletion.objects.filter(
                    lesson=leccion,
                    enrollment=enrollment,
                    completed_at__isnull=False
                ).exists()
                if completada:
                    completed_lessons += 1
                total_lessons += 1

        progreso = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        completado = progreso == 100

        # Solo agregar cursos completados
        if completado:
            certificados.append({
                'course_title': curso.title,
                'completed': completado,
            })

    return {'certificados_usuario': certificados}
