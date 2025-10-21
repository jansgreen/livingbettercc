from django.contrib import admin
from .models import ReportAccountMinerd, Campo


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(ReportAccountMinerd)
class ReportAccountMinerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'centro_educativo', 'regional', 'mostrar_campos')
    list_filter = ('regional', 'campos', 'fecha')
    search_fields = ('titulo', 'centro_educativo', 'responsabilidades', 'temas_impartidos')
    ordering = ('-fecha',)

    def mostrar_campos(self, obj):
        """Muestra los campos relacionados en una sola columna."""
        return ", ".join([campo.nombre for campo in obj.campos.all()])
    mostrar_campos.short_description = "Campos"
