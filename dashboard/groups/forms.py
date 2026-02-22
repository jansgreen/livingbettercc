from django import forms
from django.contrib.auth.models import Group, Permission

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

    def __init__(self, *args, **kwargs):
        group_queryset = kwargs.pop('group_queryset', None)
        super().__init__(*args, **kwargs)
        if group_queryset is None:
            group_queryset = Group.objects.all()
        self.fields['group'].queryset = group_queryset
