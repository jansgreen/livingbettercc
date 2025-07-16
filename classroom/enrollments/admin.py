
# Register your models here.
# enrollments/admin.py

from django.contrib import admin
from .models import Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress', 'completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('completed', 'enrolled_at')
