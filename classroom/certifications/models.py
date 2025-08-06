from django.db import models
from classroom.enrollments.models import Enrollment

# Create your models here.
# models.py
import uuid

class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_shareable_url(self):
        from django.urls import reverse
        return reverse('certificate_public_view', kwargs={'uuid': str(self.uuid)})

    def __str__(self):
        return f"Certificado de {self.enrollment.user.username} para {self.enrollment.course.title}"

        