from django import forms
from authentication.address.models import Address
from .models.profiles import Profiles
from .models.customers import Customers
from .models.students import Students
from .models.staffs import Staffs
from .models.directives import Directives
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from authentication.address.models import Address
import os


ALLOWED_CURRICULUM_EXTENSIONS = {'.pdf', '.doc', '.docx'}
ALLOWED_EVIDENCE_EXTENSIONS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
BLOCKED_ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz'}


def _validate_uploaded_extension(uploaded_file, *, allowed_extensions, field_label: str):
    if not uploaded_file:
        return uploaded_file
    extension = os.path.splitext(uploaded_file.name or '')[1].lower()
    if extension in BLOCKED_ARCHIVE_EXTENSIONS:
        raise forms.ValidationError(
            f"{field_label}: los archivos comprimidos no son compatibles. "
            f"Sube el documento descomprimido en formato {', '.join(sorted(allowed_extensions))}."
        )
    if extension not in allowed_extensions:
        raise forms.ValidationError(
            f"{field_label}: formato no permitido. "
            f"Usa uno de estos formatos: {', '.join(sorted(allowed_extensions))}."
        )
    return uploaded_file

def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()
   
class ProfileForm(forms.ModelForm):
    class MultipleFileInput(forms.ClearableFileInput):
        allow_multiple_selected = True

    class MultipleFileField(forms.FileField):
        def clean(self, data, initial=None):
            single_file_clean = super().clean
            if isinstance(data, (list, tuple)):
                return [single_file_clean(d, initial) for d in data]
            return [single_file_clean(data, initial)] if data else []

    tipo_evidencia_academica = forms.ChoiceField(
        choices=[('', 'Seleccionar tipo de evidencia')] + [
            ('certificacion', 'Certificacion'),
            ('diploma', 'Diploma'),
            ('licenciatura', 'Licenciatura'),
        ],
        required=False,
        label='Tipo de evidencia academica',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    evidencias_academicas = MultipleFileField(
        required=False,
        label='Evidencias academicas',
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True})
    )


    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'class': 'form-control',
                'placeholder': 'dd/mm/aaaa',
            }
        ),
        label='Fecha de nacimiento'
    )

    class Meta:
        model = Profiles
        exclude = ['user', 'old_cart', 'direccion']  # Adjust fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'fecha_nacimiento' in self.fields:
            self.fields['fecha_nacimiento'].widget.attrs.update({
                'placeholder': 'dd/mm/aaaa',
                'inputmode': 'numeric',
            })
        if 'imagen' in self.fields:
            self.fields['imagen'].label = 'Foto de Perfil'
        if 'curriculum_vitae' in self.fields:
            self.fields['curriculum_vitae'].label = 'Hoja de vida (Curriculum vitae)'
            self.fields['curriculum_vitae'].required = True
        if 'nivel_academico' in self.fields:
            self.fields['nivel_academico'].label = 'Nivel Academico'
            self.fields['nivel_academico'].required = True
        if 'estado_academico' in self.fields:
            self.fields['estado_academico'].label = 'Estado Academico'
            self.fields['estado_academico'].required = True

        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')

    def clean(self):
        cleaned_data = super().clean()
        nivel = cleaned_data.get('nivel_academico')
        estado = cleaned_data.get('estado_academico')
        evidence_type = cleaned_data.get('tipo_evidencia_academica')
        evidence_files = cleaned_data.get('evidencias_academicas') or []
        existing_evidence = False

        if self.instance and self.instance.pk:
            existing_evidence = self.instance.academic_evidences.exists()

        requires_evidence = nivel in {'tecnico', 'universitario'} and estado == 'graduado'

        if requires_evidence and not evidence_files and not existing_evidence:
            self.add_error('evidencias_academicas', 'Debes subir al menos una evidencia academica.')
        if evidence_files and not evidence_type:
            self.add_error('tipo_evidencia_academica', 'Selecciona el tipo de evidencia academica.')

        return cleaned_data

    def clean_curriculum_vitae(self):
        return _validate_uploaded_extension(
            self.cleaned_data.get('curriculum_vitae'),
            allowed_extensions=ALLOWED_CURRICULUM_EXTENSIONS,
            field_label='Hoja de vida',
        )

    def clean_evidencias_academicas(self):
        files = self.cleaned_data.get('evidencias_academicas') or []
        validated_files = []
        for uploaded_file in files:
            validated_files.append(
                _validate_uploaded_extension(
                    uploaded_file,
                    allowed_extensions=ALLOWED_EVIDENCE_EXTENSIONS,
                    field_label='Evidencias academicas',
                )
            )
        return validated_files

class CustomerForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Customers
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        # Address creation is handled in the view
        Customers.objects.create(user=user)
        return user

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staffs
        fields = '__all__'  # Adjust fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')

class DirectivesForm(forms.ModelForm):
    class Meta:
        model = Directives
        fields = ('__all__')  # Ensure 'biografia' is included

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Accept the user as a parameter
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')

class BootstrapUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

class BootstrapAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')
