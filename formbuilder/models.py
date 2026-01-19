import uuid
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from authentication.address.models import Address
from django.conf import settings
from django.db import models



class FormDefinition(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Backward compatible single image (legacy). Prefer image_left/image_right in UI.
    image = models.ImageField(upload_to='form_images/', blank=True, null=True)
    image_left = models.ImageField(upload_to='form_images/', blank=True, null=True)
    image_right = models.ImageField(upload_to='form_images/', blank=True, null=True)

    def __str__(self):
        return self.name


FIELD_TYPES = [
    ('char', 'Campo de texto'),
    ('email', 'Correo electrónico'),
    ('integer', 'Número entero'),
    ('text', 'Área de texto'),
    ('boolean', 'Casilla de verificación'),
    ('select', 'Selección'),
    ('files', 'Anexos (múltiples archivos)'),
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

class CompletedForm(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    form_name = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    form_data = models.JSONField()
    distrito = models.CharField(max_length=100, blank=True, null=True, help_text="Distrito del facilitador")
    address = models.ForeignKey("address.Address", null=True, blank=True, on_delete=models.SET_NULL,) 
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CompletedForm by {self.user.username} for {self.form_name} at {self.submitted_at}"
    

class FormShareLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    form = models.ForeignKey("FormDefinition", on_delete=models.CASCADE, related_name="share_links")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.form.name} ({self.token})"
