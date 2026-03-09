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


class QuickTestDefinition(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='quicktest_definition')
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"QuickTestDef for {self.module.title}"


class QuickTestQuestion(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "mcq", "Selección múltiple"
        TEXT = "text", "Respuesta escrita"
        SIGNATURE = "signature", "Firma por nombre completo"

    definition = models.ForeignKey(QuickTestDefinition, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=16, choices=QuestionType.choices, default=QuestionType.MULTIPLE_CHOICE)
    option_a = models.CharField(max_length=255, blank=True, default="")
    option_b = models.CharField(max_length=255, blank=True, default="")
    option_c = models.CharField(max_length=255, blank=True, default="")
    option_d = models.CharField(max_length=255, blank=True, default="")
    correct_option = models.CharField(max_length=1, blank=True, default="", choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])
    expected_text = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Q: {self.text[:40]}..."
