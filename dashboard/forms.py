from django import forms
from dashboard.models import CategoriaMenu, MenuItem

class CategoriaMenuForm(forms.ModelForm):
    class Meta:
        model = CategoriaMenu
        fields = ['nombre']  # Replace 'name' with actual fields in CategoriaMenu

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['categoria', 'nombre', 'url_name', 'orden']
