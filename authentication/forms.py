from django import forms
from .models.address import Address
from .models.profiles import Profiles
from .models.customers import Customers
from .models.students import Students
from .models.staffs import Staffs
from django.contrib.auth.models import User


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = '__all__'  # Adjust fields as needed

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profiles
        fields = '__all__'  # Adjust fields as needed

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


class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = '__all__'  # Adjust fields as needed

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staffs
        fields = '__all__'  # Adjust fields as needed
