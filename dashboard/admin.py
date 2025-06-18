from django.contrib import admin
from .models import CategoriaMenu, MenuItem

# Register your models here.


@admin.register(CategoriaMenu)
class CategoriaMenuAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'url_name', 'orden')
    search_fields = ('nombre', 'categoria__nombre', 'url_name')
    list_filter = ('categoria',)
    ordering = ('orden',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categoria')
