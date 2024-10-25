from django.db import models
from django.contrib.auth.models import User

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.CharField(max_length=255)
    estado = models.CharField(max_length=50, default='pendiente')  # Ej: pendiente, completado

    def __str__(self):
        return f'Orden #{self.id} por {self.usuario.username}'
