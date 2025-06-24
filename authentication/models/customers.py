from django.db import models
from django.contrib.auth.models import User, Group
from .address import Address
from .profiles import Profiles

class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Profiles = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Customers: {self.user.username}"

def assign_customers_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="customers")
        instance.groups.add(group)

models.signals.post_save.connect(assign_customers_group, sender=User)
