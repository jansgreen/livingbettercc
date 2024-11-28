from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class PageCategory(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la categoría
    description = models.TextField(blank=True, help_text="Categoría de la página")
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Si el slug está vacío, genera uno basado en el campo name
        if not self.slug and self.name:
            self.slug = slugify(self.name.replace(" ", "_").lower())  # Sustituye espacios por "_"
        super().save(*args, **kwargs)  # Llama al método save del padre

    def __str__(self):
        return self.name

class PagePosition(models.Model):
    category = models.ForeignKey(PageCategory, on_delete=models.CASCADE, related_name='positions')  # Relaciona la posición con la categoría
    row = models.IntegerField(blank=True, default=None)
    column = models.IntegerField(blank=True, default=None)  # Número de la columna
    description = models.TextField(blank=True, help_text="Descripción opcional de la columna")

    def __str__(self):
        return f"Posición en {self.category.name} - Fila: {self.row}, Columna: {self.column}"

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
    category = models.ForeignKey(PageCategory, on_delete=models.CASCADE, related_name='content', default=None)  # Relación con Column
    position = models.ForeignKey(PagePosition, on_delete=models.CASCADE, related_name='content_positions', default=None)  # Relación con Column
    cover_image = models.ImageField(upload_to='pageContentImages/', blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Etiquetas separadas por comas")

    def summary(self, char_limit=300):
        if len(self.content) == char_limit:
            return self.content
        end = self.content.rfind(' ', 0, char_limit)
        return self.content[:end] + '... Leer Mas'

    def save(self, *args, **kwargs):
        # Asignar el valor de excerpt utilizando la función summary
        if not self.excerpt:  # Solo asignar si el campo excerpt está vacío
            self.excerpt = self.summary()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class carouselPage(models.Model):
    name = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='pageImg/')
    details =  models.CharField(max_length=100, blank=True, default=None)

    def __str__(self):
        return self.name
 
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

