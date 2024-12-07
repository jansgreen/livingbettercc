from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Biography, Direccion
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm

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
    # Campos adicionales o modificados
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Nombres',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre y segundo nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'imagen',
            'genero',
            'fecha_nacimiento',
            'telefono',
            'numero_identidad',
            'profesion',
            'roll',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_identidad': forms.TextInput(attrs={'class': 'form-control'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Permite pasar el usuario al formulario
        super().__init__(*args, **kwargs)
        if user:
            # Inicializar los campos first_name y last_name desde el usuario
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        # Guardar cambios en el modelo Profile y User
        profile = super().save(commit=False)
        user = profile.user  # Obtener el usuario relacionado
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()  # Guardar cambios en User
            profile.save()  # Guardar cambios en Profile
        return profile

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['calle_y_casa', 'sector_o_barrio', 'municipio', 'provincia', 'codigo_postal']
        widgets = {
            'calle_y_casa': forms.TextInput(attrs={'class': 'form-control'}),
            'sector_o_barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.HiddenInput(attrs={'class': 'form-control'}),
            'provincia': forms.HiddenInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.HiddenInput(attrs={'class': 'form-control'}),
        }

class BiographyForm(forms.ModelForm):
    
    class Meta:
        model = Biography
        fields = ['biography']
    
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['placeholder'] = "Introduce una breve biografía."
            self.fields[field].help_text = (
                "Estructura sugerida:\n"
                "1. Introducción: Nombre, fecha de nacimiento y contribuciones.\n"
                "2. Infancia y educación: Primeros años y educación.\n"
                "3. Carrera y logros: Trayectoria y logros.\n"
                "4. Vida personal: Relaciones y su influencia.\n"
                "5. Contribuciones y legado: Impacto en la sociedad.\n"
                "6. Conclusión: Resumen y reflexión.\n"
                "7. Referencias: Fuentes utilizadas.")

            self.fields[field].widget.attrs['class'] = 'form-control'

class ChangePasswordForm(SetPasswordForm):
	class Meta:
		model = User
		fields = ['new_password1', 'new_password2']

	def __init__(self, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

		self.fields['new_password1'].widget.attrs['class'] = 'form-control'
		self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['new_password1'].label = ''
		self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['new_password2'].widget.attrs['class'] = 'form-control'
		self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['new_password2'].label = ''
		self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'