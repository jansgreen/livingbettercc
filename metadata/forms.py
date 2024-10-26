from django import forms
from .models import MetaData


class MetaDataForm(forms.ModelForm):
    class Meta:
        model = MetaData
        fields = ['title', 'description', 'keywords', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
