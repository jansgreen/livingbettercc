from django.db import models
from django.contrib.auth.models import User
from .address import Address
from .profiles import Profiles

class Staffs(models.Model):
    Profiles = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    NIVEL_CHOICES = [
        ('admin', 'Administrador'),
        ('editor', 'Editor'),
        ('colaborador', 'Colaborador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    nivel_acceso = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    biografia = models.TextField(blank=True)

    def __str__(self):
        return f"Staff: {self.user.username} ({self.nivel_acceso})"
