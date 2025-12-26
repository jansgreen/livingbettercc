# forms.py
from django import forms
from .models import Product, Category, SubCategory


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Permite pasar el usuario al formulario
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'slug']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['name', 'category']
