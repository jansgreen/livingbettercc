from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    a_type = (
        ('laboral', 'Laboral'),
        ('residencial', 'Residencial'),
        ('otro', 'Otro'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_type = models.CharField(max_length=20, choices=a_type, default='residencial')
    street = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"
