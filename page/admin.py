from django.contrib import admin
from .models import Footer, PageContent, ImagenPage, CategoryImages

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'email_contacto', 'telefono_contacto')

class PageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'status', 'category', 'cover_image')
    list_filter = ('status', 'author', 'category', 'cover_image')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'excerpt': ('content',)}
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'author', 'category', 'cover_image', 'tags', 'status', 'excerpt')
        }),
        # Eliminar el grupo de fechas, ya que no se necesitan los campos auto manejados
    )


class ImagenPageInline(admin.TabularInline):
    model = ImagenPage
    extra = 1  # Número de formularios vacíos que se mostrarán

class CategoryImagesAdmin(admin.ModelAdmin):
    inlines = [ImagenPageInline]

admin.site.register(CategoryImages, CategoryImagesAdmin)
admin.site.register(PageContent, PageContentAdmin)

