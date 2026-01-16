from django.contrib import admin
from .models import ReportActivity, ReportCategories


@admin.register(ReportActivity)
class ReportActivityAdmin(admin.ModelAdmin):
    list_display = ('course', 'issued_year', 'district', 'quantity', 'created_at')
    search_fields = ('course__title', 'district')
    list_filter = ('issued_year', 'course')
    ordering = ('-issued_year', 'course')
    readonly_fields = ('created_at',)

@admin.register(ReportCategories)
class ReportCategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('name',)