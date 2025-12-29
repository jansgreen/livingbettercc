from django.contrib import admin
from .models import Certificate, InPersonCertificateIssue

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('user', 'course', 'certificate_number', 'issued_date', 'public_uuid')
	search_fields = ('user__username', 'course__title', 'certificate_number')
	list_filter = ('issued_date', 'course')
	readonly_fields = ('certificate_number', 'issued_date', 'public_uuid')
	ordering = ('-issued_date',)


@admin.register(InPersonCertificateIssue)
class InPersonCertificateIssueAdmin(admin.ModelAdmin):
	list_display = ('course', 'issued_date', 'district', 'quantity', 'created_by')
	search_fields = ('course__title', 'district', 'created_by__username')
	list_filter = ('issued_date', 'course', 'district')
	ordering = ('-issued_date',)
