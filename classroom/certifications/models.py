from django.db import models

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from classroom.courses.models import Course

def certificate_upload_to(instance, filename):
    return f'certificates/user_{instance.user.id}/{filename}'

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates', default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates', default=1)
    certificate_number = models.CharField(max_length=64, unique=True, default="TEMP-CERT")
    issued_date = models.DateField(default=timezone.now)
    public_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pdf_file = models.FileField(upload_to=certificate_upload_to, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return f'Certificado {self.certificate_number} - {self.user.username} - {self.course.title}'

    def get_public_url(self):
        from django.urls import reverse
        return reverse('certifications:certificate_public_view', kwargs={'uuid': str(self.public_uuid)})

    def get_download_url(self):
        from django.urls import reverse
        return reverse('certifications:certificate_pdf_download', kwargs={'uuid': str(self.public_uuid)})

        