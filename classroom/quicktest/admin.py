from django.contrib import admin
from .models import QuickTest, QuickTestDefinition, QuickTestQuestion

@admin.register(QuickTest)
class QuickTestAdmin(admin.ModelAdmin):
    list_display = ('module', 'user', 'score', 'completed_at')
    search_fields = ('user__username', 'module__title')
    list_filter = ('module', 'completed_at')


class QuickTestQuestionInline(admin.TabularInline):
    model = QuickTestQuestion
    extra = 1


@admin.register(QuickTestDefinition)
class QuickTestDefinitionAdmin(admin.ModelAdmin):
    list_display = ('module', 'title')
    search_fields = ('module__title', 'title')
    inlines = [QuickTestQuestionInline]
