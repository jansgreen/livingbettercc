from django.db import models
from django.contrib.auth.models import User
from .address import Address

class Students(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    degree = models.CharField(max_length=100)
    certifications = models.TextField(blank=True)

    def __str__(self):
        return f"Estudiante: {self.user.username}"
