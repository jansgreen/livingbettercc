from django import forms
from .models import MetaData

class MetaDataForm(forms.ModelForm):
    class Meta:
        model = MetaData
        fields = ['title', 'description', 'keywords', 'category', 'search_image', 'icon']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'search_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'icon': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
