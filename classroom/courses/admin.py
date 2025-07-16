# Register your models here.
from django.contrib import admin
from .models import Course, Module, Lesson, Test, Question

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'published', 'created_at')
    list_filter = ('published', 'created_at')
    search_fields = ('title', 'description')
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title',)
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    search_fields = ('title',)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'module')
    search_fields = ('title',)
    list_filter = ('module',)   

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'correct_option')
    search_fields = ('text',)
    list_filter = ('test',)


