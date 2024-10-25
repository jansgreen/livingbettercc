from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# forms.py

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control my-custom-input-class',
            'placeholder': 'Ingresa tu correo electrónico',
            'id': 'id_email',  # Asegúrate de usar el ID correcto
            'required': True,  # Agrega el atributo "required" si es necesario
        })
    )

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control my-custom-input-class',
            'placeholder': 'Ingresa tu nombre de usuario',
            'id': 'id_username',  # Asegúrate de usar el ID correcto
            'required': True,  # Agrega el atributo "required" si es necesario
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control my-custom-input-class',
            'placeholder': 'Ingresa tu contraseña',
            'id': 'password1',  # Asegúrate de usar el ID correcto
            'required': True,  # Agrega el atributo "required" si es necesario
        })
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control my-custom-input-class',
            'placeholder': 'Confirma tu contraseña',
            'id': 'password2',  # Asegúrate de usar el ID correcto
            'required': True,  # Agrega el atributo "required" si es necesario
        })
    )

    class Meta:
        model = User  # Utiliza el modelo de usuario predeterminado
        fields = ('username', 'email', 'password1', 'password2')  # Incluye los campos necesarios

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form.
    """
    username = forms.CharField(label='Nombre de usuario', 
        widget=forms.TextInput(attrs={
            'class': 'form-control my-custom-input-class',
            'placeholder': 'Ingresa tu nombre de usuario',
            'id': 'id_username',  # Asegúrate de usar el ID correcto
            'required': True,  # Agrega el atributo "required" si es necesario
            }),
        max_length=150)
    password = forms.CharField(label='Contraseña', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control my-custom-input-class',
            'placeholder': 'Ingresa tu contraseña',
            'id': 'password1',  # Asegúrate de usar el ID correcto
            'required': True,  # Agrega el atributo "required" si es necesario
        }))

    class Meta:
        model = User  # Assuming you're using the built-in User model
        fields = ('username', 'password')

class Profileforms(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre', help_text='* NOTA: Escribe tus nonombresmbre tal como esta en tus documentos, una vez que lo hayas guardado no podrá editarlo.'
)
    last_name = forms.CharField(max_length=30, required=True, label='Apellido', help_text='* NOTA: Procura escribir tu apellidos tal como esta en tus documentos, una vez que lo hayas guardado no podrá editarlo.'
)

    fecha_nacimiento = forms.DateField(
        required=True, 
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',  # Clase para estilo Bootstrap
            'placeholder': 'Fecha de Nacimiento'
        }),
        label='Fecha de Nacimiento'
    )

    class Meta:
        model = Profile
        exclude = (
            'user',
            )
            
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Primer Nombre y Segundo Nombre',
            'last_name': 'Primer apellido y Segundo apellido',
            'telefono': 'Tu numero de telefono',
            'calle_y_casa': 'Escribe el nombre de la calle y el numero de tu casa',
            'sector_o_barrio': 'Escribe el Barrio o el sector',
            'municipio': 'Tu Municipio',
            'provincia': 'Tu Probincia',
            'codigo_postal': 'Tu codigo postal',
            'numero_identidad': 'Cedula de Identidad', 
            'imagen': 'Foto de perfil',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'genero': 'Genero',
            'profession': 'Profession',
        }

        for field in self.fields:
            if field not in ['profession','imagen','numero_identidad', ]:
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'

            elif field== 'genero':
                self.fields[field].widgets = {'genero': forms.Select(choices=Profile.GENERO_CHOICES),}
                self.fields['genero'].widget.attrs['placeholder'] = 'Selecciona tu género'
                self.fields['genero'].widget.attrs['class'] = 'form-control'
            
            elif field == 'imagen':
                # Aplicar clase específica para el campo de imagen
                self.fields['imagen'].widget.attrs['class'] = 'form-control-file'

            elif field == 'fecha_nacimiento':
                # Asegura que el campo de fecha tenga el widget correcto
                self.fields[field].widget.attrs['class'] = 'form-control'
                self.fields[field].widget.attrs['type'] = 'date'

            else:
                placeholder = f'{placeholders[field]} (Opcional)'
                self.fields[field].widget.attrs['placeholder'] = placeholder

            if field in [ 'provincia','municipio', 'codigo_postal']:
                self.fields[field].widget.attrs['class'] = 'visually-hidden-focusable'
                self.fields[field].widget.attrs['value'] = 'N/A'

            else:
                self.fields[field].widget.attrs['class'] = 'form-control mb-3'
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['aria-label'] = 'Sizing example input'
            self.fields[field].widget.attrs['aria-describedby'] = 'inputGroup-sizing-sm'
            self.fields[field].label = False
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = self.cleaned_data.get('user')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')

        if commit:
            user.save()
            profile.save()
        return profile
