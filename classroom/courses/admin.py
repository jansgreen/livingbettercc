# Register your models here.
from django.contrib import admin
from .models import Course, CourseYearStat, Program, ProgramYearStat, Module, Lesson

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class CourseYearStatInline(admin.TabularInline):
    model = CourseYearStat
    extra = 0


class ProgramYearStatInline(admin.TabularInline):
    model = ProgramYearStat
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'price', 'published', 'manual_certified_add', 'created_at')
    list_filter = ('program', 'published', 'created_at')
    search_fields = ('title', 'description')
    inlines = [CourseYearStatInline, ModuleInline]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ProgramYearStatInline]


@admin.register(ProgramYearStat)
class ProgramYearStatAdmin(admin.ModelAdmin):
    list_display = ('program', 'year', 'in_person_certified', 'estimated_children_impacted', 'updated_at')
    list_filter = ('program', 'year')
    search_fields = ('program__name', 'notes')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    search_fields = ('title',)
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    search_fields = ('title',)

 