from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class Column(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la columna
    description = models.TextField(blank=True, help_text="Descripción opcional de la columna")

    def __str__(self):
        return self.name

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

class PageContent(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()  # Editor de texto enriquecido para el contenido
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    excerpt = models.TextField(blank=True, null=True)  # Campo opcional para el extracto
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('published', 'Published')],
        default='draft'
    )
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='contents')  # Relación con Column
    tab = models.CharField(max_length=50, choices=[('home', 'Home'), ('about', 'About Us'), ('services', 'Services'), ('contact', 'Contact')])
    tags = models.CharField(max_length=100, blank=True, help_text="Etiquetas separadas por comas")
    
    def save(self, *args, **kwargs):
        # Generar automáticamente el excerpt si no se proporciona
        if not self.excerpt:
            self.excerpt = self.content[:300]  # Los primeros 150 caracteres del contenido
        super(PageContent, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

