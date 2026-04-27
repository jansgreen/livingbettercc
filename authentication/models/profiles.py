import os
from django.db import models
from django.contrib.auth.models import User
from authentication.address.models import Address
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field


class Profiles(models.Model):
    NIVEL_ACADEMICO_CHOICES = [
            ('basico', 'Estudio Basico'),
            ('secundario', 'Estudio Secundario'),
            ('tecnico', 'Estudio Tecnico'),
            ('universitario', 'Estudio Universitario'),
            ]
    ESTADO_ACADEMICO_CHOICES = [
            ('graduado', 'Graduado'),
            ('no_graduado', 'No graduado'),
            ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add fields from the related User model
    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

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
    nivel_academico = models.CharField(max_length=20, choices=NIVEL_ACADEMICO_CHOICES, blank=True, null=True)
    estado_academico = models.CharField(max_length=20, choices=ESTADO_ACADEMICO_CHOICES, blank=True, null=True)
    imagen = models.ImageField(upload_to='profiles/', default='profiles/default.jpg') 
    curriculum_vitae = models.FileField(upload_to='profiles/cv/', blank=True, null=True)
    direccion = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='Direcciones')
    old_cart = models.JSONField(default=dict, blank=True, null=True)  # Assuming this is a JSON field for cart data
    def __str__(self):
        return self.user.username


class AcademicEvidence(models.Model):
    EVIDENCE_TYPE_CHOICES = [
            ('certificacion', 'Certificacion'),
            ('diploma', 'Diploma'),
            ('licenciatura', 'Licenciatura'),
            ]

    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name='academic_evidences')
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPE_CHOICES)
    file = models.FileField(upload_to='profiles/evidencias_academicas/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-uploaded_at',)

    def __str__(self):
        return f"{self.profile.user.username} - {self.get_evidence_type_display()}"


class ScholarshipStudentInfo(models.Model):
    COUNTRY_CHOICES = [
            ('republica_dominicana', 'Republica Dominicana'),
            ('estados_unidos', 'Estados Unidos'),
            ('canada', 'Canada'),
            ('mexico', 'Mexico'),
            ('colombia', 'Colombia'),
            ('venezuela', 'Venezuela'),
            ('argentina', 'Argentina'),
            ('chile', 'Chile'),
            ('peru', 'Peru'),
            ('ecuador', 'Ecuador'),
            ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='scholarship_info')
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    district = models.PositiveIntegerField()
    regional = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_complete(self):
        return bool(self.country and self.district and self.regional and self.province)

    def save(self, *args, **kwargs):
        if self.province:
            province = self.province.strip()
            self.province = province[:1].upper() + province[1:].lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.get_country_display()}"

def profile_image_upload_path(instance, filename):
    product_name = instance.product.nombre
    ext = filename.split('.')[-1] 
    new_filename = f"{product_name}.{ext}"
    return os.path.join('Profile', new_filename)

class ProfileImage(models.Model):
    product = models.ForeignKey(Profiles, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=profile_image_upload_path)

    def clean(self):
        # Validación para limitar el número de imágenes por producto a 5
        if self.product.images.count() >= 5:
            raise ValidationError("No puedes  agregar más de 5 imágenes para este producto.")

    class Meta:
        unique_together = ('product', 'image') 

class Biography(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    biography = CKEditor5Field('Biografia', config_name='extends')

    def summary(self, char_limit=100):
        if len(self.content) <= char_limit:
            return self.content
        end = self.content.rfind(' ', 0, char_limit)
        return self.content[:end] + '... leer mas'

    def __str__(self):
        return self.user.username

