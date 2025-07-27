from django import forms
from authentication.models import Students, profiles
from django.contrib.auth.models import User


class studentRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class StudentByDistrictForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ('__all__')
        exclude = ('user', 'pendiente')  # Exclude fields that should not be displayed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'cedula': 'Cedula',
            'telefono': 'Telefono',
            'regional': 'Regional',
            'distrito_educativo': 'Distrito Educativo',
            'genero': 'Genero',
            'cargo': 'Cargo',
            'institucion_laboral': 'Institucion Laboral'
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
            if field_name in placeholders:
                field.widget.attrs.setdefault('placeholder', placeholders[field_name])



