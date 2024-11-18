from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
class blogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return self.name

class blogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    content = RichTextField(verbose_name="Contenido")
    category = models.ForeignKey(blogCategory, on_delete=models.CASCADE, related_name="posts", verbose_name="Categoría")
    cover_image = models.ImageField(upload_to='gallery/cover_images/', blank=True, null=True, verbose_name="Imagen de Portada")
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/', blank=True, null=True, verbose_name="Miniatura")
    use_thumbnail_as_cover = models.BooleanField(default=False, verbose_name="Usar Miniatura como Portada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    def summary(self, char_limit=300):
        if len(self.content) == char_limit:
            return self.content
        end = self.content.rfind(' ', 0, char_limit)
        return self.content[:end] + '...'

    def __str__(self):
        return self.title
