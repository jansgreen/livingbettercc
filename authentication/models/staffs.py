from django.db import models
from django.contrib.auth.models import User
from .address import Address
from .profiles import Profiles
from django.db.models.signals import post_save
from django.dispatch import receiver

class Staffs(models.Model):
    Profiles = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Staff: {self.user.username} ({self.nivel_acceso})"

@receiver(post_save, sender=Staffs)
def activate_staff_status(sender, instance, created, **kwargs):
    if created:
        instance.user.is_staff = True
        instance.user.save()
