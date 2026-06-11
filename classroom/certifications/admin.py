from django.contrib import admin

from .models import Certificate, OnlineCertificateReport

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('cert_no', 'user', 'course', 'issued_date')
	search_fields = ('cert_no', 'user__username', 'course__title')
	list_filter = ('issued_date',)


@admin.register(OnlineCertificateReport)
class OnlineCertificateReportAdmin(admin.ModelAdmin):
	list_display = ('course', 'issued_year', 'total_quantity', 'is_closed', 'sync_enabled', 'created_at')
	search_fields = ('course__title', 'districts_list', 'regional_list', 'province_list')
	list_filter = ('issued_year', 'is_closed', 'sync_enabled', 'created_at')
	ordering = ('-issued_year', 'course')

