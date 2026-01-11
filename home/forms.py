from django import forms
from .models import ReportActivity

class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))


class ReportActivityForm(forms.ModelForm):
    class Meta:
        model = ReportActivity
        fields = ['course', 'issued_year', 'district', 'quantity', 'image', 'description']

        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'issued_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Regional Norte'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

                