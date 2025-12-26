from django import forms
from .models import ContentCategory, ContentPost


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()

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
            _append_css_class(field.widget, 'form-control')

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
            _append_css_class(field.widget, 'form-control')
            if field_name == 'description':
                field.widget.attrs.update({'rows': 3})
