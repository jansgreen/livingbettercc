from django.contrib import admin
from .models import FormDefinition, FormField, FormShareLink, SystemFormAssignment

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1

@admin.register(FormDefinition)
class FormDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    filter_horizontal = ('assigned_groups',)
    inlines = [FormFieldInline]
    
@admin.register(FormShareLink)
class FormShareLinkAdmin(admin.ModelAdmin):
    list_display = ('form', 'token', 'created_by', 'is_active', 'created_at')
    list_filter = ('form', 'is_active', 'created_at')
    
@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'form', 'field_type', 'order')
    list_filter = ('form', 'field_type')

@admin.register(SystemFormAssignment)
class SystemFormAssignmentAdmin(admin.ModelAdmin):
    list_display = ('key', 'updated_at')
    filter_horizontal = ('assigned_groups',)
