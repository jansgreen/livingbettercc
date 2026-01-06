from django.db import models
from django.contrib.auth.models import User
from authentication.address.models import Address
from .profiles import Profiles
from django.db.models.signals import post_save
from django.dispatch import receiver

class Staffs(models.Model):
    # Renombrado de 'Profiles' a 'profile' (convención lowercase)
    profile = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Cambiado a ForeignKey para permitir múltiples direcciones
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='staffs')

    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'

    def __str__(self):
        return f"Staff: {self.user.username}"

@receiver(post_save, sender=Staffs)
def activate_staff_status(sender, instance, created, **kwargs):
    if created:
        instance.user.is_staff = True
        instance.user.save()
