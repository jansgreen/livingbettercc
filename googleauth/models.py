from django.db import models
from django.contrib.auth.models import User

class StudentProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_id = models.CharField(max_length=50, unique=True)
    completed_modules = models.JSONField(default=list)  # Lista de módulos completados
    exam_scores = models.JSONField(default=dict)  # {"module_1": 85, "module_2": 90}

    def __str__(self):
        return self.user.username

# Create your models here.
