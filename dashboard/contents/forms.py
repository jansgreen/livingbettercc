from django import forms
from .models import ContentCategory, ContentPost

class ContentPostForm(forms.ModelForm):
    class Meta:
        model = ContentPost
        fields = ['title', 'slug', 'content', 'status', 'cover_image', 'category', 'section', 'tags']
        widgets = {
            'status': forms.Select(),  # usa Select para mostrar las opciones
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply a consistent `form-control` class to all visible fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        # Field-specific widget tweaks (only if the field exists)
        if 'content' in self.fields:
            try:
                self.fields['content'].widget.attrs.update({'rows': 5})
            except Exception:
                pass
        if 'tags' in self.fields:
            try:
                self.fields['tags'].widget.attrs.update({'placeholder': 'Separate tags with commas'})
            except Exception:
                pass

class ContentCategoryForm(forms.ModelForm):
    class Meta:
        model = ContentCategory
        fields = ['name', 'slug', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'description':
                field.widget.attrs.update({'rows': 3})
