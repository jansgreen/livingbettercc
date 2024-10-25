from django.contrib import admin
from .models import CategoriaProducto, Producto, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Número de formularios vacíos que se mostrarán

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'categoria')
    search_fields = ('nombre', 'categoria__nombre')
    list_filter = ('categoria',)
    inlines = [ProductImageInline]  # Incluye imágenes en la administración del producto

class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

# Registra los modelos en el admin
admin.site.register(CategoriaProducto, CategoriaProductoAdmin)
admin.site.register(Producto, ProductoAdmin)
