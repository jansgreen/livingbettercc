from django.contrib import admin
from .models import carouselPage, Page, PageSection


class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'show_in_navbar', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'parent', 'show_in_navbar', 'order')
        }),
    )

class PageSectionAdmin(admin.ModelAdmin):

    list_display = ('page', 'name', 'row', 'column', 'zone')
    ordering = ('page', 'name', 'row', 'column')
    fieldsets = (
        (None, {
            'fields': ('page', 'name', 'row', 'column', 'zone')
        }),
    )

class carouselPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'imagen', 'details')
    ordering = ('-name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'imagen', 'details')
        }),
        # Eliminar el grupo de fechas, ya que no se necesitan los campos auto manejados
    )

admin.site.register(carouselPage, carouselPageAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageSection, PageSectionAdmin)

