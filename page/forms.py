from django import forms
from .models import Footer, PageContent, Column, CategoryImages, ImagenPage, pageCategory

class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'  # Incluye todos los campos del modelo Footer


class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ['title', 'content', 'category', 'tags', 'cover_image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),

        }



class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['category', 'num', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'num': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la columna'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción opcional'}),
        }


class pageCategoryForm(forms.ModelForm):
    class Meta:
        model = pageCategory
        fields = ['name', 'description', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción opcional'}),
        }



class CategoryImgForm(forms.ModelForm):
    class Meta:
        model = CategoryImages
        fields = ['nombre']

class ImagenPageForm(forms.ModelForm):
    class Meta:
        model = ImagenPage
        fields = ['category', 'imagen', 'details']
