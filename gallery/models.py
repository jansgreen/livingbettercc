from django.db import models

# Create your models here.

class Image(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image_file = models.ImageField(upload_to='gallery/')
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Aquí podrías añadir lógica para generar la miniatura
