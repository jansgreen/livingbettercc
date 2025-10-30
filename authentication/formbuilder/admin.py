from django.contrib import admin
from .models import FormDefinition, FormField

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1

@admin.register(FormDefinition)
class FormDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    inlines = [FormFieldInline]

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'form', 'field_type', 'order')
    list_filter = ('form', 'field_type')
