from django.db import models

class Footer(models.Model):
    titulo = models.CharField(max_length=100, default="#")
    mision = models.TextField()
    enlace_inicio = models.URLField(max_length=200, default="#")
    enlace_quienes_somos = models.URLField(max_length=200, default="#")
    enlace_contacto = models.URLField(max_length=200, default="#")
    enlace_galeria = models.URLField(max_length=200, default="#")
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=15)
    derechos_autor = models.CharField(max_length=255, default="© 2024 Living Better Community Center. Todos los derechos reservados.")

    def __str__(self):
        return self.titulo

# Create your models here.
