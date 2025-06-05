from django import forms
from .models.address import Address
from .models.profiles import Profiles
from .models.customers import Customers
from .models.students import Students
from .models.staffs import Staffs

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'  # Adjust fields as needed

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profiles
        fields = '__all__'  # Adjust fields as needed

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customers
        fields = '__all__'  # Adjust fields as needed

class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = '__all__'  # Adjust fields as needed

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staffs
        fields = '__all__'  # Adjust fields as needed
