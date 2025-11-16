from django.db import models
from django.conf import settings
from classroom.courses.models import Module

class QuickTest(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quicktests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quicktests')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)
    # Add more fields as needed (questions, answers, etc)

    def __str__(self):
        return f"QuickTest {self.module.title} - {self.user.username} ({self.score})"