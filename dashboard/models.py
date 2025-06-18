from django.db import models
from django.urls import reverse

class CategoriaMenu(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Categoría de Menú'
        verbose_name_plural = 'Categorías de Menús'

    def __str__(self):
        return self.nombre

class MenuItem(models.Model):
    categoria = models.ForeignKey(CategoriaMenu, related_name='menus', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    url_name = models.CharField(max_length=100, help_text="Nombre de la vista para usar con {% url %}")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    def get_url(self):
        try:
            return reverse(self.url_name)  # esto devuelve /contactanos/
        except:
            return "#"

