from django.contrib import admin
from .models import Profile, Biography, Direccion

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    readonly_fields = (
        'user',
        'telefono', 
        )
    fields = (
    'user',  
    'telefono', 
    'numero_identidad', 
    'imagen', 
    'fecha_nacimiento', 
    'genero', 
    'profesion',
    'roll',
        )
    list_display = (
    'user',  
    'telefono', 
    'imagen', 
    'fecha_nacimiento', 
    'genero', 
    'profesion',
    'roll',

    )

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('calle_y_casa', 'sector_o_barrio', 'municipio', 'provincia', 'codigo_postal',)

@admin.register(Biography)
class BiographyAdmin(admin.ModelAdmin):
    readonly_fields = (
        'user',
        )
    list_display = ('user',)

# Registra los modelos en el admin

