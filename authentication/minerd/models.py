from django.db import models

# Create your models here.


class Campo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Campo"
        verbose_name_plural = "Campos"

    def __str__(self):
        return self.nombre


class ReportAccountMinerd(models.Model):
    titulo = models.CharField(max_length=200)
    subtitulo = models.CharField(max_length=250, blank=True, null=True)
    centro_educativo = models.CharField(max_length=200)
    responsabilidades = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    temas_impartidos = models.TextField(blank=True, null=True)
    objetivo_razon_motivo = models.TextField(blank=True, null=True)
    regional = models.CharField(max_length=150)
    campos = models.ManyToManyField(Campo, related_name='reportes')
    documentos = models.FileField(upload_to='reportes_minerd/', blank=True, null=True)

    class Meta:
        verbose_name = "Reporte MINERD"
        verbose_name_plural = "Reportes MINERD"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.titulo} - {self.centro_educativo}"



