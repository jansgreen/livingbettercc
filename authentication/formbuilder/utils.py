# formbuilder/utils.py
from django import forms
from .models import FormDefinition, FormField

def generate_dynamic_form(form_name):
    try:
        form_def = FormDefinition.objects.get(name=form_name)
    except FormDefinition.DoesNotExist:
        return None

    fields = {}
    for field in form_def.fields.all():
        field_args = {'label': field.label, 'required': field.required}

        if field.field_type == 'char':
            fields[field.name] = forms.CharField(**field_args)
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(**field_args)
        elif field.field_type == 'integer':
            fields[field.name] = forms.IntegerField(**field_args)
        elif field.field_type == 'text':
            fields[field.name] = forms.CharField(widget=forms.Textarea, **field_args)
        elif field.field_type == 'boolean':
            fields[field.name] = forms.BooleanField(**field_args)
        elif field.field_type == 'select':
            choices = [(c.strip(), c.strip()) for c in field.choices.split(',')]
            fields[field.name] = forms.ChoiceField(choices=choices, **field_args)

    # Crear una clase Form dinámica
    DynamicForm = type(f"{form_name}Form", (forms.Form,), fields)
    return DynamicForm
