from django import forms
from .models.address import Address
from .models.profiles import Profiles
from .models.customers import Customers
from .models.students import Students
from .models.staffs import Staffs
from .models.directives import Directives
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'address_type', 'street', 'neighborhood', 'city', 'state', 'zip_code']  # Exclude user field to be set in the view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# me quede aqui, tengo que trabajar con la logica de los datos personales y la certificacion

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

            field.widget.attrs.update({'class': 'form-control'})

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
            field.widget.attrs.update({'class': 'form-control'})

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
            field.widget.attrs.update({'class': 'form-control'})

class DirectivesForm(forms.ModelForm):
    class Meta:
        model = Directives
        fields = ('__all__')  # Ensure 'biografia' is included

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Accept the user as a parameter
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class BootstrapUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
