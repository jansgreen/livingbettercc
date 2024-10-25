from django import forms
from .models import Footer

class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'  # Incluye todos los campos del modelo Footer
