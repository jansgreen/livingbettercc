from django.contrib import admin
from .models import PostStatus, Categoria, Posicion, Post

class PostStatusAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class PosicionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_creacion', 'categoria', 'estatus')
    list_filter = ('categoria', 'estatus', 'fecha_creacion')
    search_fields = ('titulo', 'contenido')
    prepopulated_fields = {'excerpt': ('contenido',)}  # Esto permite que el campo excerpt se complete automáticamente basado en el contenido
    readonly_fields = ('fecha_creacion',)

admin.site.register(PostStatus, PostStatusAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Posicion, PosicionAdmin)
admin.site.register(Post, PostAdmin)
