from django.contrib import admin
from .models import Footer

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'email_contacto', 'telefono_contacto')

# Register your models here.
