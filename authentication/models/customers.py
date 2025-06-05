from django.db import models
from django.contrib.auth.models import User
from .address import Address
from .profiles import Profiles

class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Profiles = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Cliente: {self.user.username}"
