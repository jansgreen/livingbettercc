from django import forms
from .models import Image


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'description', 'image_file', 'forcarousel']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "forcarousel":
                field.label = "¿Mostrar en carrusel?"
                field.widget.attrs.update({'class': 'form-check-input', 'id':"forcarouselCheck"})
            else:
                _append_css_class(field.widget, 'form-control')