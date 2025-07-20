
# Register your models here.
# enrollments/admin.py

from django.contrib import admin
from .models import Enrollment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress', 'completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    list_filter = ('completed', 'enrolled_at')

from django.contrib import admin
from .models import ModuleCompletion, LessonCompletion

@admin.register(ModuleCompletion)
class ModuleCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'module', 'completed_at')
    list_filter = ('completed_at', 'module__course')
    search_fields = ('enrollment__user__username', 'module__title', 'module__course__title')
    autocomplete_fields = ('enrollment', 'module')
    ordering = ('-completed_at',)

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed_at')
    list_filter = ('completed_at', 'lesson__module__course')
    search_fields = ('enrollment__user__username', 'lesson__title', 'lesson__module__title')
    autocomplete_fields = ('enrollment', 'lesson')
    ordering = ('-completed_at',)
