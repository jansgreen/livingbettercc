import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

def product_image_upload_path(instance, filename):
    product_name = instance.product.nombre
    image_count = instance.product.images.count()
    image_number = image_count + 1 
    ext = filename.split('.')[-1] 
    new_filename = f"{product_name}_{image_number}.{ext}"
    return os.path.join('productos', new_filename)

class ProductImage(models.Model):
    product = models.ForeignKey(Producto, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_upload_path)

    def clean(self):
        # Validación para limitar el número de imágenes por producto a 5
        if self.product.images.count() >= 5:
            raise ValidationError("No puedes agregar más de 5 imágenes para este producto.")

    class Meta:
        unique_together = ('product', 'image')  # Asegura que no haya imágenes duplicadas para un mismo producto.


class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ItemCarrito')

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre}"