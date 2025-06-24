from django import forms
from authentication.models.address import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'neighborhood', 'city', 'state', 'zip_code']
