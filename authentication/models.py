import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    GENERO_CHOICES = [
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=10)
    calle_y_casa = models.CharField(max_length=120, blank=True, null=True)
    sector_o_barrio = models.CharField(max_length=120, blank=True, null=True)
    municipio = models.CharField(max_length=120, blank=True, null=True)
    provincia = models.CharField(max_length=120, blank=True, null=True)
    codigo_postal = models.IntegerField(blank=True, null=True)
    numero_identidad = models.CharField(max_length=11, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)
    profesion = models.CharField(max_length=140, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(upload_to='Profile/', default='profiles/default.jpg')

    def __str__(self):
        return self.user.username
  
def profile_image_upload_path(instance, filename):
    product_name = instance.product.nombre
    ext = filename.split('.')[-1] 
    new_filename = f"{product_name}.{ext}"
    return os.path.join('Profile', new_filename)

class ProfileImage(models.Model):
    product = models.ForeignKey(Profile, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=profile_image_upload_path)

    def clean(self):
        # Validación para limitar el número de imágenes por producto a 5
        if self.product.images.count() >= 5:
            raise ValidationError("No puedes agregar más de 5 imágenes para este producto.")

    class Meta:
        unique_together = ('product', 'image') 

class Biography(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    biography = models.TextField()
    excerpt = models.TextField(blank=True, null=True)  # Campo opcional para el extracto


    def save(self, *args, **kwargs):
        # Generar automáticamente el excerpt si no se proporciona
        if not self.excerpt:
            self.excerpt = self.biography[:100]  # Los primeros 150 caracteres del contenido
        super(Biography, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Biography"
