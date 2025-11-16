from django import forms
from django.utils.text import slugify
from .models import FormDefinition, FormField


class FormDefinitionForm(forms.ModelForm):
    class Meta:
        model = FormDefinition
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'description' in self.fields:
            self.fields['description'].widget.attrs.update({'rows': 4})
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


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
            field.widget.attrs.update({'class': 'form-control'})
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
