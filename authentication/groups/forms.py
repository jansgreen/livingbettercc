from django import forms
from django.contrib.auth.models import Group, Permission
from authentication.models.profiles import ScholarshipStudentInfo
from formbuilder.system_forms import SCHOLARSHIP_STUDENT_INFO_KEY, get_group_ids_for_system_form


def _capitalize_province(value):
    value = (value or '').strip()
    if not value:
        return value
    return value[:1].upper() + value[1:].lower()

class GroupForm(forms.Form):
    group = forms.ChoiceField(
        choices=[],  # Inicialmente vacío
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Asigna un grupo'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_groups = Group.objects.all()
        self.fields['group'].choices = [(group.id, group.name) for group in available_groups]

class PermissionForm(forms.Form):
    permissions = forms.MultipleChoiceField(
        choices=[],  # Inicialmente vacío
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Selecciona los permisos'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_permissions = Permission.objects.all()
        self.fields['permissions'].choices = [(permission.id, f"{permission.content_type.app_label}/{permission.name}") for permission in available_permissions]


class PermissionForm(forms.Form):
    permissions = forms.MultipleChoiceField(
        choices=[],  # Inicialmente vacío
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Selecciona los permisos'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_permissions = Permission.objects.all()
        self.fields['permissions'].choices = [(permission.id, f"{permission.content_type.app_label}/{permission.name}") for permission in available_permissions]


class GroupFormCreate(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
                    'name': forms.TextInput(attrs={'class': 'col-3 form-control'}),
                }

class InviteForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    group = forms.ModelChoiceField(queryset=Group.objects.none(), widget=forms.Select(attrs={'class': 'form-control'}))
    scholarship_country = forms.ChoiceField(
        choices=[('', 'Seleccionar pais')] + ScholarshipStudentInfo.COUNTRY_CHOICES,
        required=False,
        label='Pais',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    scholarship_regional = forms.CharField(
        max_length=255,
        required=False,
        label='Regional',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Regional 10'})
    )
    scholarship_district = forms.IntegerField(
        min_value=1,
        required=False,
        label='Distrito',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1001'})
    )
    scholarship_province = forms.CharField(
        max_length=255,
        required=False,
        label='Provincia',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Santo Domingo'})
    )

    def __init__(self, *args, **kwargs):
        group_queryset = kwargs.pop('group_queryset', None)
        scholarship_group_ids = kwargs.pop('scholarship_group_ids', None)
        super().__init__(*args, **kwargs)
        if group_queryset is None:
            group_queryset = Group.objects.all()
        self.fields['group'].queryset = group_queryset
        if scholarship_group_ids is None:
            scholarship_group_ids = get_group_ids_for_system_form(SCHOLARSHIP_STUDENT_INFO_KEY)
        self.scholarship_group_ids = {int(group_id) for group_id in scholarship_group_ids}

    def clean(self):
        cleaned_data = super().clean()
        group = cleaned_data.get('group')
        is_scholarship = bool(group and group.id in self.scholarship_group_ids)
        province = cleaned_data.get('scholarship_province')
        if province:
            cleaned_data['scholarship_province'] = _capitalize_province(province)

        if is_scholarship:
            required_fields = (
                'scholarship_country',
                'scholarship_regional',
                'scholarship_district',
                'scholarship_province',
            )
            for field_name in required_fields:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'Este campo es obligatorio para estudiantes becados.')

        return cleaned_data


class ScholarshipStudentInfoForm(forms.ModelForm):
    class Meta:
        model = ScholarshipStudentInfo
        fields = ['country', 'regional', 'district', 'province']
        labels = {
            'country': 'Pais',
            'regional': 'Regional',
            'district': 'Distrito',
            'province': 'Provincia',
        }
        widgets = {
            'country': forms.Select(attrs={'class': 'form-control'}),
            'regional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Regional 10'}),
            'district': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1001'}),
            'province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Santo Domingo'}),
        }

    def clean_province(self):
        return _capitalize_province(self.cleaned_data.get('province'))
