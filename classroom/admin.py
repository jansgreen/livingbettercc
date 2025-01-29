from django.contrib import admin
from .models import Course, Module, Lesson, Material

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('course', 'created_at')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'created_at')
    search_fields = ('title', 'module__title')
    list_filter = ('module', 'created_at')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('file', 'type', 'lesson', 'created_at')
    search_fields = ('file', 'type', 'lesson__title')
    list_filter = ('lesson', 'created_at')
