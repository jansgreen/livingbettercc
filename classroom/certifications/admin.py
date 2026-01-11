from django.contrib import admin

from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('cert_no', 'user', 'course', 'issued_date')
	search_fields = ('cert_no', 'user__username', 'course__title')
	list_filter = ('issued_date',)

