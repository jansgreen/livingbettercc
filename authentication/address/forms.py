from django import forms
from .models import Address 
from authentication.forms import _append_css_class
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

