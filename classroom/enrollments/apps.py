# classroom/courses/apps.py

from django.apps import AppConfig

class EnrollmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classroom.enrollments'
    label = 'enrollments'  # 👈 Esto define cómo Django la ve internamente
