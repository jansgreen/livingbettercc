from django.contrib import admin
from .models import Footer, PageContent

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'email_contacto', 'telefono_contacto')

class PageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'status', 'column', 'tab')
    list_filter = ('status', 'author', 'column', 'tab')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'excerpt': ('content',)}
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author', 'column', 'tab', 'tags', 'status', 'excerpt')
        }),
        # Eliminar el grupo de fechas, ya que no se necesitan los campos auto manejados
    )

admin.site.register(PageContent, PageContentAdmin)
