from django.db import models
from django.contrib.auth.models import User, Group
from .address import Address
from .profiles import Profiles

class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Renombrado de 'Profiles' a 'profile' (convención lowercase)
    profile = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    # Cambiado a ForeignKey para permitir múltiples direcciones (aunque típicamente se usa una)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"Cliente: {self.user.username}"

# Signal corregido: conectado a Customers en lugar de User
def assign_customers_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="customers")
        instance.user.groups.add(group)

models.signals.post_save.connect(assign_customers_group, sender=Customers)
