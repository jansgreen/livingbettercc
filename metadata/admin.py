from django.contrib import admin
from .models import MetaData

@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description', 'keywords')
