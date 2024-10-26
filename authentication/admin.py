from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    readonly_fields = (
        'user',
        'telefono', 
        'calle_y_casa',  
        'sector_o_barrio',
        )

    fields = (
    'user',  
    'telefono', 
    'calle_y_casa',  
    'sector_o_barrio', 
    'municipio', 
    'provincia',
    'codigo_postal', 
    'numero_identidad', 
    'imagen', 
    'fecha_nacimiento', 
    'genero', 
    'profession',
    'puesto',
        )
    
    list_display = (
    'user',  
    'telefono', 
    'calle_y_casa',  
    'sector_o_barrio', 
    'municipio', 
    'provincia',
    'codigo_postal', 
    'numero_identidad', 
    'imagen', 
    'fecha_nacimiento', 
    'genero', 
    'profesion',
    'puesto',

    )

# Registra los modelos en el admin
admin.site.register(Profile, ProfileAdmin)
