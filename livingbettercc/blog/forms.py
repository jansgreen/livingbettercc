from django import forms
from .models import Post, Categoria, Posicion

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'categoria', 'posicion', 'estatus']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
            self.fields['contenido'].widget.attrs.update({
            'style': 'width: 100%; height: 420px;',
        })

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {
            'Categoria': forms.TextInput(attrs={'class': 'form-control'})
        }
 
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        return nombre.capitalize()

class PosicionForm(forms.ModelForm):
    class Meta:
        model = Posicion
        fields = ['nombre']
        widgets = {
            'nombre': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Solo numeros'})
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        # Aplicar patrón específico: column-X
        nombre_transformado = f'column-{nombre}'
        return nombre_transformado

