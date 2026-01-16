from django import forms
from .models import ReportActivity, ReportCategories

class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))


class ReportActivityForm(forms.ModelForm):
    class Meta:
        model = ReportActivity
        fields = ['course', 'issued_year', 'district', 'quantity', 'image', 'description', 'categories']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                if 'image' in field:
                    self.fields[field].widget.attrs.update({'type': 'file', 'class': 'form-control', 'id': 'formFile'})
                if 'categories' in field:
                    self.fields[field].widget.attrs.update({'class': 'form-select'})
                else:
                    self.fields[field].widget.attrs.update({'class': 'form-control'})


class ReportCategoriesForm(forms.ModelForm):
    class Meta:
        model = ReportCategories
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

