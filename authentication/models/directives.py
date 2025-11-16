from django.db import models
from django.contrib.auth.models import User, Group  # Import Group
from django.apps import apps  # Importa apps para usar get_model
from .address import Address
from .profiles import Profiles
from ckeditor.fields import RichTextField  # Asegúrate de tener django-ckeditor instalado


class Directives(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=150, null=True, verbose_name="Cargo")  # Ej: "Director General"
    foto = models.ImageField(upload_to="directiva_fotos/", null=True, blank=True, verbose_name="Foto")
    # Renombrado de 'profiles' a 'profile' para consistencia
    profile = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    # Cambiado a ForeignKey para permitir múltiples direcciones
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='directives')
    biografia = RichTextField(verbose_name="Biografía", null=True, blank=True)

    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn")

    class Meta:
        verbose_name = 'Directivo'
        verbose_name_plural = 'Directivos'

    def summary(self, char_limit=150):
        """Devuelve un resumen de la biografía truncado a char_limit caracteres"""
        if not self.biografia or len(self.biografia) <= char_limit:
            return self.biografia or ""
        end = self.biografia.rfind(' ', 0, char_limit)
        if end == -1:
            end = char_limit
        return self.biografia[:end] + '...'

    def __str__(self):
        return f"Directivo: {self.user.username} - {self.cargo or 'Sin cargo'}"


#asigna un grupo a los Directives al crearlos
def assign_Directives_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="Directives")
        instance.user.groups.add(group)

models.signals.post_save.connect(assign_Directives_group, sender=Directives)
