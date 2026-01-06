# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    a_type = (
        ('laboral', 'Laboral'),
        ('residencial', 'Residencial'),
        ('otro', 'Otro'),
    )
    # Cambiado de OneToOneField a ForeignKey para permitir múltiples direcciones por usuario
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=a_type, default='residencial')
    street = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # Asegurar que no se dupliquen direcciones del mismo tipo para un usuario
        unique_together = [['user', 'address_type']]
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return f"{self.get_address_type_display()} - {self.street or 'Sin calle'}, {self.city or 'Sin ciudad'}"
