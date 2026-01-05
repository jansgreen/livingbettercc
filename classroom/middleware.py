from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings


class RequireActiveEnrollmentMiddleware(MiddlewareMixin):
    """
    Bloquea acceso académico (módulos, lecciones, tests, descarga de certificados)
    cuando la matrícula del usuario en el curso no está en estado ACTIVE.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Necesitamos usuario autenticado para evaluar matrícula
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        match = getattr(request, 'resolver_match', None)
        if not match:
            return None

        url_name = match.view_name or ''
        path = getattr(request, 'path', '') or ''

        # Allowlist: do not intercept admin, static, media, webhook
        if path.startswith('/admin/'):
            return None
        if settings.STATIC_URL and path.startswith(settings.STATIC_URL):
            return None
        if settings.MEDIA_URL and path.startswith(settings.MEDIA_URL):
            return None
        if url_name == 'enrollments:stripe_webhook':
            return None

        protected = {
            'courses:module_detail',
            'courses:lesson_detail',
            'courses:quicktest',
            'courses:next_module',
            'certifications:certificate_pdf_download',
        }

        if url_name not in protected:
            return None

        # Resolver el curso asociado a la vista protegida
        from classroom.courses.models import Module, Lesson
        from classroom.enrollments.models import Enrollment

        course = None
        try:
            if url_name in ('courses:module_detail', 'courses:next_module'):
                module_id = view_kwargs.get('pk') or view_kwargs.get('module_id')
                if module_id:
                    module = Module.objects.select_related('course').only('course_id').get(pk=module_id)
                    course = module.course
            elif url_name == 'courses:quicktest':
                module_id = view_kwargs.get('module_id')
                if module_id:
                    module = Module.objects.select_related('course').only('course_id').get(pk=module_id)
                    course = module.course
            elif url_name == 'courses:lesson_detail':
                lesson_id = view_kwargs.get('pk')
                if lesson_id:
                    lesson = Lesson.objects.select_related('module__course').only('module__course_id').get(pk=lesson_id)
                    course = lesson.module.course
            elif url_name == 'certifications:certificate_pdf_download':
                # Descarga de certificado: la validación de completion debe existir a nivel de vista.
                # Aquí solo bloqueamos si la matrícula no está ACTIVE para el curso del certificado.
                # Si la vista no provee contexto, se permitirá y la vista debe validar.
                return None
        except (Module.DoesNotExist, Lesson.DoesNotExist):
            return None

        if not course:
            return None

        enrollment = Enrollment.objects.filter(user=user, course=course).first()
        if not enrollment or enrollment.status != Enrollment.Status.ACTIVE:
            messages.error(request, 'Tu matrícula no está activa para este curso.')
            return redirect('courses:my_course')

        return None
