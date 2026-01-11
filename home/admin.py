from django.contrib import admin
from .models import ReportActivity


@admin.register(ReportActivity)
class ReportActivityAdmin(admin.ModelAdmin):
    list_display = ('course', 'issued_year', 'district', 'quantity', 'created_at')
    search_fields = ('course__title', 'district')
    list_filter = ('issued_year', 'course')
    ordering = ('-issued_year', 'course')
    readonly_fields = ('created_at',)
