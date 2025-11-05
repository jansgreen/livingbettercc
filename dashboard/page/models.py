from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify

from django.db import models
from django.utils.text import slugify

class Page(models.Model):
    """
    Represents a website page (Home, About, Blog, etc.).
    Defines the logical grouping of content sections.
    """
    name = models.CharField("Page Name", max_length=100, unique=True)
    slug = models.SlugField("Slug", unique=True)
    description = models.TextField("Description", blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subpages",
        help_text="Optional parent page for nested navigation."
    )
    show_in_navbar = models.BooleanField(default=True, help_text="Display this page in the main navigation menu.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PageSection(models.Model):
    """
    Defines a visual section of a Page (row or column).
    Example: Hero, Highlights, News Area, Footer widgets.
    """
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField("Section Name", max_length=100)
    row = models.PositiveIntegerField(default=1)
    column = models.PositiveIntegerField(default=1)
    zone = models.CharField("Zone", max_length=100, blank=True, help_text="Optional visual identifier (e.g., 'header', 'sidebar').")

    class Meta:
        verbose_name = "Page Section"
        verbose_name_plural = "Page Sections"
        ordering = ["page", "row", "column"]

    def __str__(self):
        return f"{self.page.name} - {self.name} (Row {self.row}, Col {self.column})"

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

