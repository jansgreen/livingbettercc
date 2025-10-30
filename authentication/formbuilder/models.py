from django.db import models

class FormDefinition(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='form_images/', blank=True, null=True)

    def __str__(self):
        return self.name


FIELD_TYPES = [
    ('char', 'Campo de texto'),
    ('email', 'Correo electrónico'),
    ('integer', 'Número entero'),
    ('text', 'Área de texto'),
    ('boolean', 'Casilla de verificación'),
    ('select', 'Selección'),
]


class FormField(models.Model):
    form = models.ForeignKey(FormDefinition, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    name = models.SlugField(help_text="Nombre interno del campo (sin espacios ni caracteres especiales)")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)
    choices = models.TextField(
        blank=True,
        null=True,
        help_text="Solo para campos tipo selección. Separar opciones por coma."
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.form.name} - {self.label}"
