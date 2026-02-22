from django.db import models
from django.contrib.auth.models import User, Group  # Import Group
from authentication.address.models import Address


class Certification(models.Model):
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='certificados/')

    def __str__(self):
        return self.nombre
class Students(models.Model):
    genero = (
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=11, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    regional = models.CharField(max_length=100, null=True, blank=True)
    por_distrito = models.BooleanField(default=False)
    distrito_educativo = models.CharField(max_length=100, null=True, blank=True)
    genero = models.CharField(max_length=10, choices=genero, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    certification = models.FileField(upload_to='Certification/', null=True, blank=True)
    institucion_laboral = models.CharField(max_length=100, null=True, blank=True)
    pendiente = models.BooleanField(default=True)

    def __str__(self):
        return f"students: {self.user.username}"

def assign_students_group(sender, instance, created, **kwargs):
    if created:
        # Use canonical plural group name.
        group, _ = Group.objects.get_or_create(name="estudiantes")
        instance.user.groups.add(group)

models.signals.post_save.connect(assign_students_group, sender=Students)
