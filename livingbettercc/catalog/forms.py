from django import forms
from .models import Producto, CategoriaProducto, ProductImage


class ProductImageForm(forms.ModelForm):
    image = forms.FileField(required=False)

    class Meta:
        model = ProductImage
        fields = ['image']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }
    categoria = forms.ModelChoiceField(queryset=CategoriaProducto.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
        }
