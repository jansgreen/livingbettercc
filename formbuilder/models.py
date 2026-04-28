import uuid
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from authentication.address.models import Address
from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group

from payments.models import User


class FormDefinition(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = CKEditor5Field('Text', config_name='extends', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Backward compatible single image (legacy). Prefer image_left/image_right in UI.
    image = models.ImageField(upload_to='form_images/', blank=True, null=True)
    image_left = models.ImageField(upload_to='form_images/', blank=True, null=True)
    image_right = models.ImageField(upload_to='form_images/', blank=True, null=True)
    assigned_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='assigned_form_definitions',
        help_text='Grupos que pueden ver y completar este formulario.',
    )

    def __str__(self):
        return self.name

    def _safe_image_url(self, field_name: str) -> str:
        field = getattr(self, field_name, None)
        if not field:
            return ""
        try:
            return field.url
        except Exception:
            return ""

    @property
    def image_left_url(self) -> str:
        return self._safe_image_url("image_left")

    @property
    def image_right_url(self) -> str:
        return self._safe_image_url("image_right")


class SystemFormAssignment(models.Model):
    SCHOLARSHIP_STUDENT_INFO = 'scholarship_student_info'

    FORM_CHOICES = [
        (SCHOLARSHIP_STUDENT_INFO, 'Datos del estudiante becado'),
    ]

    key = models.CharField(max_length=100, choices=FORM_CHOICES, unique=True)
    assigned_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='assigned_system_forms',
        help_text='Grupos para los que se activa este formulario del sistema.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return self.get_key_display()

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
    name = models.SlugField(
        help_text="Nombre interno del campo (sin espacios ni caracteres especiales)",
        blank=True,
    )
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
    form = models.ForeignKey("FormDefinition", null=True, blank=True, on_delete=models.SET_NULL)
    form_name = models.CharField(max_length=255)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    form_data = models.JSONField()
    distrito = models.CharField(max_length=100, blank=True, null=True, help_text="Distrito del facilitador")
    address = models.ForeignKey("address.Address", null=True, blank=True, on_delete=models.SET_NULL,) 
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        form_name = self.form.name if self.form else self.form_name
        return f"CompletedForm by {self.user.username} for {form_name} at {self.submitted_at}"

class FormShareLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    form = models.ForeignKey("FormDefinition", on_delete=models.CASCADE, related_name="share_links")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.form.name} ({self.token})"

    def is_valid(self) -> bool:
        # No expiration policy; only active links are valid.
        return self.is_active

class EducationalCenter(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    number = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    distrito = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ImpactsBefore(models.Model):
    school_disappointment = models.IntegerField()
    family_conflict = models.IntegerField()
    dysfunctional_homes = models.IntegerField()
    health_problems = models.IntegerField()
    mental_health_problems = models.IntegerField()

class ImpactsPositive(models.Model):
    school_level = models.IntegerField()
    family_level = models.IntegerField()
    social = models.IntegerField()
    improvement_in_school_disappointment = models.IntegerField()

class attached_files(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class TrimestralReport(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    educational_center = models.ForeignKey(EducationalCenter, on_delete=models.SET_NULL, null=True, blank=True)
    attached_files = models.ManyToManyField(attached_files, blank=True)
    name = models.CharField(max_length=255, unique=True)
    tittle = models.TextField(blank=True, null=True)
    distrite = models.CharField(max_length=100, blank=True, null=True, help_text="Distrito del facilitador")
    goals = models.TextField(blank=True, null=True)
    methodology = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=50, choices=[('male', 'Masculino'), ('female', 'Femenino')], blank=True, null=True)
    trimestre = models.CharField(max_length=20)
    year = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

