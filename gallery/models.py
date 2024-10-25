import os
from django.conf import settings
from django.db import models



def product_image_upload_path(instance, filename):
    return os.path.join('products', str(instance.product.id), filename)

def post_image_upload_path(instance, filename):
    return os.path.join('posts', str(instance.post.id), filename)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to=user_profile_image_upload_path, blank=True, null=True)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('CategoriaProducto', on_delete=models.CASCADE)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_upload_path)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=post_image_upload_path)
