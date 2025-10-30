from django import forms
from .models import FormDefinition, FormField

class FormDefinitionForm(forms.ModelForm):
    class Meta:
        model = FormDefinition
        fields = ['name', 'description']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['description'].widget.attrs.update({'rows': 4})

            for field in self.fields.values():
                field.widget.attrs.update({'class': 'form-control'})

class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ['form', 'label', 'name', 'field_type', 'required', 'choices', 'order']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['choices'].widget.attrs.update({'rows': 4})

            for field in self.fields.values():
                field.widget.attrs.update({'class': 'form-control'})
