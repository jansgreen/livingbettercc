from django.db import models
from django.conf import settings
from authentication.models.address import Address

class BecaApplication(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    cedula = models.CharField(max_length=11)
    exequatur = models.CharField(max_length=100)
    centro_educativo = models.CharField(max_length=255)
    distrito_escolar = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='beca_applications')
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')


    def __str__(self):
        return f"Beca Minerd: {self.user.username} - {self.course.title} ({self.estado})"
# enrollments/models.py

from django.db import models
from django.conf import settings

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course')
        ]

    def __str__(self):
        return f"{self.user.username} in {self.course.title}"


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
