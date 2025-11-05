from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from dashboard.page.models import Page, PageSection  # Ajusta si tu app de pages tiene otro nombre

User = get_user_model()

class ContentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True, verbose_name="Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría de Contenido"
        verbose_name_plural = "Categorías de Contenido"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ContentPost(models.Model):
    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("published", "Publicado"),
        ("archived", "Archivado"),
    ]

    # --- Campos principales ---
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    content = RichTextField(verbose_name="Contenido")

    # --- Relaciones ---
    category = models.ForeignKey(ContentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts", verbose_name="Categoría")
    page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, blank=True, related_name="contents", verbose_name="Página")
    section = models.ForeignKey(PageSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="contents", verbose_name="Sección de Página")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="contents", verbose_name="Autor")

    # --- Multimedia ---
    cover_image = models.ImageField(upload_to="gallery/cover_images/", blank=True, null=True, verbose_name="Imagen de Portada")
    thumbnail = models.ImageField(upload_to="gallery/thumbnails/", blank=True, null=True, verbose_name="Miniatura")
    use_thumbnail_as_cover = models.BooleanField(default=False, verbose_name="Usar Miniatura como Portada")

    # --- Metadatos ---
    tags = models.CharField(max_length=255, blank=True, verbose_name="Etiquetas (separadas por comas)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    # --- Propiedades dinámicas ---
    @property
    def image(self):
        """Retorna la imagen de portada o la miniatura según preferencia."""
        if self.use_thumbnail_as_cover and self.thumbnail:
            return self.thumbnail.url
        elif self.cover_image:
            return self.cover_image.url
        return None

    def summary(self, char_limit=300):
        """Devuelve un resumen seguro del contenido (sin cortar a mitad de palabra)."""
        clean_text = str(self.content).replace("<p>", "").replace("</p>", "")
        if len(clean_text) <= char_limit:
            return clean_text
        end = clean_text.rfind(" ", 0, char_limit)
        return clean_text[:end] + "..."

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while ContentPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Contenido"
        verbose_name_plural = "Contenidos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"
