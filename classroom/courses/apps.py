# classroom/courses/apps.py

from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classroom.courses'
    label = 'courses'  # 👈 Esto define cómo Django la ve internamente
