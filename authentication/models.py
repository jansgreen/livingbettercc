import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    GENERO_CHOICES = [
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=10)
    numero_identidad = models.CharField(max_length=11, blank=True, null=True)
    profesion = models.CharField(max_length=140, blank=True, null=True)
    roll = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')
    direccion = models.ForeignKey('Direccion', on_delete=models.SET_NULL, null=True, blank=True, related_name='Direcciones')
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Direccion(models.Model):
    calle_y_casa = models.CharField(max_length=120, blank=True, null=True)
    sector_o_barrio = models.CharField(max_length=120, blank=True, null=True)
    municipio = models.CharField(max_length=120, blank=True, null=True)
    provincia = models.CharField(max_length=120, blank=True, null=True)
    codigo_postal = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.calle_y_casa}, {self.sector_o_barrio}, {self.municipio}, {self.provincia}"

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    biography = RichTextField(verbose_name="Biografia")

    def summary(self, char_limit=100):
        if len(self.content) <= char_limit:
            return self.content
        end = self.content.rfind(' ', 0, char_limit)
        return self.content[:end] + '... leer mas'

    def __str__(self):
        return self.user.username

