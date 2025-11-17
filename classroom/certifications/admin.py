from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('user', 'course', 'certificate_number', 'issued_date', 'public_uuid')
	search_fields = ('user__username', 'course__title', 'certificate_number')
	list_filter = ('issued_date', 'course')
	readonly_fields = ('certificate_number', 'issued_date', 'public_uuid')
	ordering = ('-issued_date',)
