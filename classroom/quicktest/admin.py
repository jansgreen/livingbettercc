from django.contrib import admin
from .models import QuickTest

@admin.register(QuickTest)
class QuickTestAdmin(admin.ModelAdmin):
    list_display = ('module', 'user', 'score', 'completed_at')
    search_fields = ('user__username', 'module__title')
    list_filter = ('module', 'completed_at')
