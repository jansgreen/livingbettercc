from django import forms
from django import forms
from .models.address import Address
from .models.profiles import Profiles
from .models.customers import Customers
from .models.students import Students
from .models.staffs import Staffs
from .models.directives import Directives
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()

class FacilitadorRegistrationForm(forms.Form):
    def clean_username(self):
        from django.contrib.auth.models import User
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'El usuario "{username}" ya existe. Por favor elige otro nombre de usuario.')
        return username
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    distrito = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Distrito')
    # Dirección: se usará AddressForm embebido
    street = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Calle y número')
    neighborhood = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Barrio o sector')
    city = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Ciudad/Provincia')
    state = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Municipio/Estado')
    zip_code = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Código postal', required=False)

    def save(self):
        from django.contrib.auth.models import User, Group
        from .models.address import Address
        # Crear usuario
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        # Asignar grupo facilitador si no existe
        group, created = Group.objects.get_or_create(name='facilitador')
        if not user.groups.filter(name='facilitador').exists():
            user.groups.add(group)
        # Crear dirección
        address = Address.objects.create(
            user=user,
            address_type='residencial',
            street=self.cleaned_data['street'],
            neighborhood=self.cleaned_data['neighborhood'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
        )
        # Retornar usuario, distrito y dirección
        return user, self.cleaned_data['distrito'], address
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'neighborhood', 'city', 'state', 'zip_code']  # Campos editables por el usuario
        # 'user' y 'address_type' se asignan en la vista

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplicar clase Bootstrap a todos los campos
        for field in self.fields.values():
            _append_css_class(field.widget, 'form-control')
        
        # Etiquetas en español
        self.fields['street'].label = 'Calle y número'
        self.fields['neighborhood'].label = 'Barrio o sector'
        self.fields['city'].label = 'Ciudad/Provincia'
        self.fields['state'].label = 'Municipio/Estado'
        self.fields['zip_code'].label = 'Código postal'
class ProfileForm(forms.ModelForm):


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

    class Meta:
        model = Profiles
        exclude = ['user', 'old_cart', 'direccion']  # Adjust fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label == 'imagen':
                field.label_suffix = 'Foto de Perfil'

            _append_css_class(field.widget, 'form-control')
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
