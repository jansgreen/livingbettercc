from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User


class PostStatus(models.Model):
    BORRADOR = 'borrador'
    PUBLICADO = 'publicado'
    ESTATUS_CHOICES = [
        (BORRADOR, 'Borrador'),
        (PUBLICADO, 'Publicado'),
    ]

    nombre = models.CharField(max_length=100, choices=ESTATUS_CHOICES, default=PUBLICADO)

    def __str__(self):
        return self

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Posicion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Cambiado a ForeignKey
    titulo = models.CharField(max_length=200)
    contenido = RichTextField()
    excerpt = models.TextField(blank=True, null=True)  # Campo opcional para el extracto
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    posicion = models.ForeignKey(Posicion, on_delete=models.CASCADE)
    estatus = models.CharField(max_length=100, choices=PostStatus.ESTATUS_CHOICES, default=PostStatus.PUBLICADO)

    def save(self, *args, **kwargs):
        # Generar automáticamente el excerpt si no se proporciona
        if not self.excerpt:
            self.excerpt = self.contenido[:300]  # Los primeros 150 caracteres del contenido
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.titulo
