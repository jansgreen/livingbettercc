from django import forms
from django.utils.text import slugify
from .models import FormDefinition, FormField


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()


class FormDefinitionForm(forms.ModelForm):
    class Meta:
        model = FormDefinition
        fields = ['name', 'description', 'image_left', 'image_right', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'description' in self.fields:
            self.fields['description'].widget.attrs.update({'rows': 4})
            _append_css_class(self.fields['description'].widget, 'django_ckeditor_5')

        if 'image' in self.fields:
            _append_css_class(self.fields['image'].widget, 'form-control')

        if 'image_left' in self.fields:
            _append_css_class(self.fields['image_left'].widget, 'form-control')

        if 'image_right' in self.fields:
            _append_css_class(self.fields['image_right'].widget, 'form-control')

        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')


class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ['form', 'label', 'name', 'field_type', 'required', 'choices', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make choices textarea taller
        if 'choices' in self.fields:
            self.fields['choices'].widget.attrs.update({'rows': 4})
        # Add bootstrap classes
        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')
        # Help text clarifying name behavior
        if 'name' in self.fields:
            self.fields['name'].help_text = 'Nombre interno (sin espacios ni caracteres especiales). Si lo dejas vacío se generará automáticamente a partir de la etiqueta.'

    def clean_name(self):
        """Ensure the stored name is a slug. If empty, generate from label."""
        name = self.cleaned_data.get('name', '')
        label = self.cleaned_data.get('label', '')
        if not name and label:
            # generate slug from label
            return slugify(label)
        # normalize provided name
        return slugify(name)
