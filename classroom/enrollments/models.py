from django.db import models
from django.conf import settings
from authentication.models.address import Address
from django.contrib.auth import get_user_model

class BecaApplication(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    cedula = models.CharField(max_length=11)
    exequatur = models.CharField(max_length=100)
    centro_educativo = models.CharField(max_length=255)
    distrito_escolar = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='beca_applications')
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='beca_reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"Beca Minerd: {self.user.username} - {self.course.title} ({self.status})"
# enrollments/models.py

from django.db import models
from django.conf import settings

class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING_APPROVAL = 'pending_approval', 'En revisión (Beca)'
        PENDING_PAYMENT  = 'pending_payment',  'Esperando pago'
        ACTIVE           = 'active',           'Activo'
        COMPLETED        = 'completed',        'Completado'
        REJECTED         = 'rejected',         'Beca rechazada'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course')
        ]

    def __str__(self):
        return f"{self.user.username} in {self.course.title} ({self.status})"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_session_id = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.user.username} - {self.course.title} ({self.status})"


class StripeEvent(models.Model):
    """Tracks processed Stripe event IDs to ensure idempotency."""
    event_id = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"StripeEvent {self.type} ({self.event_id})"


class ModuleCompletion(models.Model):
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    module = models.ForeignKey('courses.Module', on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'module')

    def __str__(self):
        return f"{self.enrollment.user.username} completed {self.module.title}"


class LessonCompletion(models.Model):
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"{self.enrollment.user.username} completed {self.lesson.title}"
