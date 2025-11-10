from django.db import models
from django.contrib.auth.models import User, Group  # Import Group
from django.apps import apps  # Importa apps para usar get_model
from .address import Address
from .profiles import Profiles
from ckeditor.fields import RichTextField  # Asegúrate de tener django-ckeditor instalado


class Directives(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=150, null=True)  # Ej: "Director General"
    foto = models.ImageField(upload_to="directiva_fotos/", null=True, blank=True)
    profiles = models.OneToOneField(Profiles, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    biografia = RichTextField(verbose_name="Biografia", null=True, blank=True)

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    def summary(self, char_limit=150):
        if len(self.biografia) <= char_limit:
            return self.biografia
        end = self.biografia.rfind(' ', 0, char_limit)
        return self.biografia[:end] + '...'

    def __str__(self):
        return f"Directives: {self.user.username}"


#asigna un grupo a los Directives al crearlos
def assign_Directives_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="Directives")
        instance.user.groups.add(group)

models.signals.post_save.connect(assign_Directives_group, sender=Directives)
