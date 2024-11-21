from django import forms
from .models import Footer, PageContent, PagePosition, carouselPage, PageCategory

class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'  # Incluye todos los campos del modelo Footer


class PageContentForm(forms.ModelForm):
    class Meta:
        model = PageContent
        fields = ['title', 'content', 'category', 'position', 'tags', 'cover_image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),

        }



class PagePositionForm(forms.ModelForm):
    class Meta:
        model = PagePosition
        fields = ['category', 'row', 'column', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'row': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'numero de la fila'}),
            'column': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'numero de la columna'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción opcional'}),
        }


class PageCategoryForm(forms.ModelForm):
    class Meta:
        model = PageCategory
        fields = ['name', 'description', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Pestaña'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción opcional'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No es obligatirio'}),

        }



class carouselPageForm(forms.ModelForm):
    class Meta:
        model = carouselPage
        fields = ['name', 'imagen', 'details']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
