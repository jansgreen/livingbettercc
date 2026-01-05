
# Register your models here.
# enrollments/admin.py

from django.contrib import admin
from .models import Enrollment, BecaApplication, Payment
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress', 'completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('status', 'completed', 'enrolled_at')
    actions = ['approve_beca', 'reject_beca', 'activate_enrollment']

    def _send_mail(self, to_email: str, subject: str, body: str):
        try:
            EmailMessage(
                subject=subject,
                body=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                to=[to_email],
            ).send(fail_silently=True)
        except Exception:
            pass

    def approve_beca(self, request, queryset):
        for enrollment in queryset:
            # Match BecaApplication for this user/course
            beca = BecaApplication.objects.filter(user=enrollment.user, course=enrollment.course).order_by('-fecha_aplicacion').first()
            if beca:
                beca.status = 'approved'
                beca.reviewed_by = request.user
                beca.reviewed_at = timezone.now()
                beca.save()
            enrollment.status = Enrollment.Status.ACTIVE
            enrollment.save()
            # Email notification
            if enrollment.user.email:
                self._send_mail(
                    enrollment.user.email,
                    'Beca aprobada',
                    f'Tu beca para {enrollment.course.title} ha sido aprobada. Ya puedes acceder al curso.'
                )
        self.message_user(request, 'Becas aprobadas y matrículas activadas.')
    approve_beca.short_description = 'Aprobar beca (activar matrícula)'

    def reject_beca(self, request, queryset):
        for enrollment in queryset:
            beca = BecaApplication.objects.filter(user=enrollment.user, course=enrollment.course).order_by('-fecha_aplicacion').first()
            if beca:
                beca.status = 'rejected'
                beca.reviewed_by = request.user
                beca.reviewed_at = timezone.now()
                beca.save()
            enrollment.status = Enrollment.Status.REJECTED
            enrollment.save()
            if enrollment.user.email:
                self._send_mail(
                    enrollment.user.email,
                    'Beca rechazada',
                    f'Tu solicitud de beca para {enrollment.course.title} fue rechazada.'
                )
        self.message_user(request, 'Becas rechazadas y matrículas actualizadas.')
    reject_beca.short_description = 'Rechazar beca (marcar matrícula)'

    def activate_enrollment(self, request, queryset):
        for enrollment in queryset:
            enrollment.status = Enrollment.Status.ACTIVE
            enrollment.save()
        self.message_user(request, 'Matrículas activadas.')
    activate_enrollment.short_description = 'Activar matrícula'

from django.contrib import admin
from .models import ModuleCompletion, LessonCompletion

@admin.register(ModuleCompletion)
class ModuleCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'module', 'completed_at')
    list_filter = ('completed_at', 'module__course')
    search_fields = ('enrollment__user__username', 'module__title', 'module__course__title')
    autocomplete_fields = ('enrollment', 'module')
    ordering = ('-completed_at',)

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed_at')
    list_filter = ('completed_at', 'lesson__module__course')
    search_fields = ('enrollment__user__username', 'lesson__title', 'lesson__module__title')
    autocomplete_fields = ('enrollment', 'lesson')
    ordering = ('-completed_at',)


@admin.register(BecaApplication)
class BecaApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'fecha_aplicacion', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'fecha_aplicacion')
    search_fields = ('user__username', 'course__title', 'cedula', 'exequatur')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrollment', 'amount', 'status', 'stripe_session_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'course__title', 'stripe_session_id')
