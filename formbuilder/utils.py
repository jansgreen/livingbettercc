"""Utilities for building and rendering dynamic forms."""

from __future__ import annotations

from django import forms

from .models import FormDefinition


def _widget_attrs(field_type: str) -> dict:
    if field_type == 'select':
        return {'class': 'form-select'}
    if field_type == 'boolean':
        return {'class': 'form-check-input'}
    if field_type == 'files':
        return {'class': 'form-control'}
    # default for input-like widgets
    return {'class': 'form-control'}


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """A FileField that accepts multiple uploaded files."""

    def clean(self, data, initial=None):
        if data in (None, '', [], ()):  # no files
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        cleaned = []
        for item in data:
            cleaned.append(super().clean(item, initial))
        return cleaned


def generate_dynamic_form(form_name: str):
    try:
        form_def = FormDefinition.objects.get(name=form_name)
    except FormDefinition.DoesNotExist:
        return None

    fields: dict[str, forms.Field] = {}
    for field in form_def.fields.all():
        field_args = {'label': field.label, 'required': field.required}
        attrs = _widget_attrs(field.field_type)

        if field.field_type == 'char':
            fields[field.name] = forms.CharField(
                widget=forms.TextInput(attrs=attrs),
                **field_args,
            )
        elif field.field_type == 'email':
            fields[field.name] = forms.EmailField(
                widget=forms.EmailInput(attrs=attrs),
                **field_args,
            )
        elif field.field_type == 'integer':
            fields[field.name] = forms.IntegerField(
                widget=forms.NumberInput(attrs=attrs),
                **field_args,
            )
        elif field.field_type == 'text':
            textarea_attrs = {**attrs, 'rows': 4}
            fields[field.name] = forms.CharField(
                widget=forms.Textarea(attrs=textarea_attrs),
                **field_args,
            )
        elif field.field_type == 'boolean':
            fields[field.name] = forms.BooleanField(
                widget=forms.CheckboxInput(attrs=attrs),
                **field_args,
            )
        elif field.field_type == 'select':
            choices_raw = field.choices or ''
            choices = [(c.strip(), c.strip()) for c in choices_raw.split(',') if c.strip()]
            fields[field.name] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs=attrs),
                **field_args,
            )
        elif field.field_type == 'files':
            fields[field.name] = MultipleFileField(
                required=field.required,
                label=field.label,
                widget=MultipleFileInput(attrs={**attrs, 'multiple': True}),
            )

    DynamicForm = type(f"{form_name}Form", (forms.Form,), fields)
    return DynamicForm


def build_ordered_responses(form_name: str, form_data: dict) -> list[dict]:
    """Return an ordered list of {name,label,value} for completed forms.

    If the form definition exists, we honor FormField.order and use labels.
    Otherwise we fall back to the JSON key order.
    """

    try:
        form_def = FormDefinition.objects.get(name=form_name)
    except FormDefinition.DoesNotExist:
        return [
            {
                'name': k,
                'label': str(k),
                'value': v,
                'is_list': isinstance(v, (list, tuple)),
            }
            for k, v in (form_data or {}).items()
        ]

    field_defs = list(form_def.fields.all())
    responses: list[dict] = []
    used_keys: set[str] = set()

    for f in field_defs:
        if not form_data or f.name not in form_data:
            value = ''
        else:
            value = form_data.get(f.name)
        responses.append(
            {
                'name': f.name,
                'label': f.label,
                'value': value,
                'is_list': isinstance(value, (list, tuple)),
            }
        )
        used_keys.add(f.name)

    # Include any extra keys (e.g. legacy fields)
    if form_data:
        for k, v in form_data.items():
            if k in used_keys:
                continue
            responses.append(
                {
                    'name': k,
                    'label': str(k),
                    'value': v,
                    'is_list': isinstance(v, (list, tuple)),
                }
            )

    return responses
