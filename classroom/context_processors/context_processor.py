from importlib.resources import path
from django.urls import reverse, NoReverseMatch
from classroom.courses.models import Course, Module, Lesson
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from classroom.enrollments.models import Enrollment, LessonCompletion, ModuleCompletion
from classroom.certifications.models import Certificate
import logging
from core.group_utils import has_group
from core.menu_builder import build_menu, safe_id

logger = logging.getLogger(__name__)

def obtener_menu_classroom(request):
    if request.user.is_authenticated:
        submenus = []

        def safe_reverse(name: str, *args, **kwargs):
            try:
                return reverse(name, args=args, kwargs=kwargs)
            except NoReverseMatch:
                return None
            except Exception:
                return None

        # Admin/staff actions gated by permission

        url_panel_aula = safe_reverse('courses:course_admin_list')
        if url_panel_aula:
            if request.user.is_superuser or request.user.is_staff:
                submenus.append({'nombre': 'Panel del Aula', 'url': url_panel_aula})
            else:
                submenus.append({'nombre': 'Panel del Aula', 'url': url_panel_aula, 'perm': 'groups.access_module'})

        url_course_list = safe_reverse('courses:course_list')

        url_certs_panel = safe_reverse('certifications:certificate_list')  # Panel de Certificaciones
        if url_certs_panel:
            submenus.append({'nombre': 'Panel de Certificaciones', 'url': url_certs_panel, 'perm': 'groups.access_module'})

        # Admin actions centralized in panels above.

        # In-person links removed; ReportActivity is managed in 'home' app.

        url_my_certs = safe_reverse('certifications:my_certificates_list')
        if url_my_certs:
            submenus.append({'nombre': 'Mis Certificados', 'url': url_my_certs, 'perm': 'groups.access_module'})

        url_users_certs = safe_reverse('certifications:users_certificate_list')
        if url_users_certs:
            submenus.append({'nombre': 'Lista de Certificados de usuarios', 'url': url_users_certs, 'perm': 'groups.access_module'})

        # Student menu (added only if user is in student group)
        try:
            is_student = has_group(request.user, [
                "estudiantes", "estudiante", "student", "students",
                "estudiantes_becados", "estudiante_becado", "estudiantes becados"
            ])
        except Exception:
            is_student = False
        if is_student:
            url_my_course = safe_reverse('courses:my_course')
            if url_my_course:
                submenus.append({'nombre': 'Mis Cursos', 'url': url_my_course})

            if url_course_list:
                submenus.append({'nombre': 'Cursos Disponibles', 'url': url_course_list})

            if url_my_course:
                submenus.append({'nombre': 'Progreso y Certificados', 'url': url_my_course})

            if url_my_course:
                submenus.append({'nombre': 'Mis Calificaciones', 'url': url_my_course})

            if url_my_certs:
                submenus.append({'nombre': 'Mis Certificados', 'url': url_my_certs})
        else:
            if url_course_list:
                submenus.append({'nombre': 'Cursos Disponibles', 'url': url_course_list})


        menu = build_menu(request.user, 'Aula Virtual', submenus, url='#')
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
    return {'Cursos en Progreso': progress}

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

def obtener_quicktest_manager(request):
    if request.user.is_authenticated:
        submenus = []

        def safe_reverse(name: str, *args, **kwargs):
            try:
                return reverse(name, args=args, kwargs=kwargs)
            except NoReverseMatch:
                return None
            except Exception:
                return None
        
        # QuickTest management
        url_quicktest_list = safe_reverse('quicktest:quicktest_list')
        if url_quicktest_list:
            submenus.append({'nombre': 'Lista de QuickTests', 'url': url_quicktest_list, 'perm': 'groups.access_module'})

        url_quicktest_create = safe_reverse('quicktest:quicktest_create')
        if url_quicktest_create:
            submenus.append({'nombre': 'Crear QuickTest', 'url': url_quicktest_create, 'perm': 'groups.access_module'})

        # QuickTest Definitions
        url_qdef_list = safe_reverse('quicktest:qdef_list')
        if url_qdef_list:
            submenus.append({'nombre': 'Definiciones de QuickTest', 'url': url_qdef_list, 'perm': 'groups.access_module'})

        url_qdef_create = safe_reverse('quicktest:qdef_create')
        if url_qdef_create:
            submenus.append({'nombre': 'Crear Definición', 'url': url_qdef_create, 'perm': 'groups.access_module'})

        # QuickTest Questions
        url_q_list = safe_reverse('quicktest:q_list', kwargs={'def_id': 0})
        if url_q_list:
            submenus.append({'nombre': 'Preguntas de QuickTest', 'url': url_q_list, 'perm': 'groups.access_module'})

        menu = build_menu(request.user, 'Menu de Examenes', submenus, url='#')
        return {'menu_quicktest': [menu] if menu else []}
    else:
        return {'menu_quicktest': []}
