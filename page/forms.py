from django import forms
from .models import Footer, PageContent, Column, CategoryImages, ImagenPage

class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'  # Incluye todos los campos del modelo Footer


class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ['title', 'content', 'author', 'column', 'tab', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'column': forms.Select(attrs={'class': 'form-control'}),
            'tab': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['name']  # Cambia esto según los campos de tu modelo Column
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la columna'}),
        }

class CategoryImgForm(forms.ModelForm):
    class Meta:
        model = CategoryImages
        fields = ['nombre']

class ImagenPageForm(forms.ModelForm):
    class Meta:
        model = ImagenPage
        fields = ['category', 'imagen', 'details']
