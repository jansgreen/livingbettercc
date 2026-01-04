from django.urls import reverse
from classroom.courses.models import Course, Module, Lesson
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from classroom.enrollments.models import Enrollment, LessonCompletion, ModuleCompletion
from classroom.certifications.models import Certificate
import logging

logger = logging.getLogger(__name__)

from core.menu_builder import build_menu, safe_id

def obtener_menu_classroom(request):
    if request.user.is_authenticated:
        submenus = []
        # Admin/staff actions gated by permission
        submenus.append({'nombre': 'Crear Curso', 'url': reverse('courses:course_create'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Lista de Cursos', 'url': reverse('courses:course_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Crear Modulo', 'url': reverse('courses:module_create'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Modulos', 'url': reverse('courses:module_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Lecciones', 'url': reverse('courses:lesson_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Crear Lección', 'url': reverse('courses:lesson_create'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Certificados Presenciales', 'url': reverse('certifications:inperson_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Registrar Presencial', 'url': reverse('certifications:inperson_create'), 'perm': 'groups.access_module'})

        # Student menu (added only if user is in student group)
        try:
            is_student = request.user.groups.filter(name__in=['student', 'students']).exists()
        except Exception:
            is_student = False
        if is_student:
            submenus.append({'nombre': 'Mis Cursos', 'url': reverse('courses:my_course')})
            submenus.append({'nombre': 'Cursos Disponibles', 'url': reverse('courses:course_list')})
            submenus.append({'nombre': 'Progreso y Certificados', 'url': reverse('courses:my_course')})
            submenus.append({'nombre': 'Mis Calificaciones', 'url': reverse('courses:my_course')})

        menu = build_menu(request.user, 'Classroom', submenus, url='#')
        return {'menu_classroom': [menu] if menu else []}
    else:
        return {'menu_classroom': []}

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
    logger.warning(f"[CTX] obtener_progress_class => {type(progress)} | {progress}")
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
        completed_modules_list = []

        for modulo in curso.modules.prefetch_related('lessons'):
            modulo_completado = True
            for leccion in modulo.lessons.all():
                completada = LessonCompletion.objects.filter(
                    lesson=leccion,
                    enrollment=enrollment,
                    completed_at__isnull=False
                ).exists()
                if not completada:
                    modulo_completado = False
                if completada:
                    completed_lessons += 1
                total_lessons += 1
            if modulo_completado:
                # Fetch QuickTest result for completed module
                from classroom.quicktest.models import QuickTest
                quicktest_result = QuickTest.objects.filter(module=modulo, user=user).order_by('-completed_at').first()
                completed_modules_list.append({
                    'module_title': modulo.title,
                    'module_id': modulo.id,
                    'course_id': curso.id,
                    'quicktest': quicktest_result,
                })

        progreso = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        completado = progreso == 100

        # Agregar todos los cursos completados, aunque no tengan certificado
        cert = Certificate.objects.filter(user=user, course=curso).first()
        cert_uuid = cert.public_uuid if cert else None
        certificados.append({
            'course_title': curso.title,
            'completed': completado,
            'certificate_uuid': str(cert_uuid) if cert_uuid else None,
            'modules': completed_modules_list,
        })
    logger.warning(f"[CTX] obtener_certificados_usuario => {type(certificados)} | {certificados}")
    return {'certificados_usuario': certificados}
