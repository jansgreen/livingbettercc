from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class pageCategory(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la categoría
    description = models.TextField(blank=True, help_text="Categoría de la página")
    slug = models.SlugField(unique=True, blank=True, null=True)  # Nuevo campo para almacenar el valor modificado

    def save(self, *args, **kwargs):
        # Convertir el nombre a minúsculas y reemplazar los espacios por guiones
        if self.name:
            self.slug = self.name.lower().replace(" ", "_")  # Asigna el valor convertido al campo 'slug'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    
class Column(models.Model):
    num = models.IntegerField(default=None)  # Número de la columna
    category = models.ForeignKey(pageCategory, on_delete=models.CASCADE, related_name="columns", default=None, null=True )
    description = models.TextField(
        blank=True, 
        help_text="Descripción opcional de la columna"
    )

    def __str__(self):
        return f"{self.num} (Categoría: {self.category.name})"

class PageContent(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()  # Editor de texto enriquecido para el contenido
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    excerpt = models.TextField(blank=True, null=True)  # Campo opcional para el extracto
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('published', 'Published'), ('pending', 'Pending')],
        default='draft'
    )
    category = models.ForeignKey(pageCategory, on_delete=models.CASCADE, related_name='catgory_page', default=None)  # Relación con Column
    cover_image = models.ImageField(upload_to='pageContentImages/', blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Etiquetas separadas por comas")

    def summary(self, char_limit=300):
        if len(self.content) == char_limit:
            return self.content
        end = self.content.rfind(' ', 0, char_limit)
        return self.content[:end] + '...'

    def save(self, *args, **kwargs):
        # Asignar el valor de excerpt utilizando la función summary
        if not self.excerpt:  # Solo asignar si el campo excerpt está vacío
            self.excerpt = self.summary()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class CategoryImages(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ImagenPage(models.Model):
    category = models.ForeignKey(CategoryImages, related_name='CategoryImages', on_delete=models.CASCADE, default=None)
    imagen = models.ImageField(upload_to='pageImg/')
    details =  models.CharField(max_length=100, blank=True, default=None)

    def __str__(self):
        return f'{self.habilidad.nombre} - Imagen'
    

class Footer(models.Model):
    titulo = models.CharField(max_length=100, default="#")
    mision = models.TextField()
    enlace_inicio = models.URLField(max_length=200, default="#")
    enlace_quienes_somos = models.URLField(max_length=200, default="#")
    enlace_contacto = models.URLField(max_length=200, default="#")
    enlace_galeria = models.URLField(max_length=200, default="#")
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=15)
    derechos_autor = models.CharField(max_length=255, default="© 2024 Living Better Community Center. Todos los derechos reservados.")

    def __str__(self):
        return self.titulo

