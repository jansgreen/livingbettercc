from django.contrib import admin

from .models import Certificate, OnlineCertificateReport

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('cert_no', 'user', 'course', 'issued_date')
	search_fields = ('cert_no', 'user__username', 'course__title')
	list_filter = ('issued_date',)


@admin.register(OnlineCertificateReport)
class OnlineCertificateReportAdmin(admin.ModelAdmin):
	list_display = ('course', 'issued_year', 'district', 'quantity')
	search_fields = ('course__title', 'district')
	list_filter = ('issued_year', 'district')
	ordering = ('-issued_year', 'district')

