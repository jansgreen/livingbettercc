from django import forms
from .models import Footer, carouselPage, Page, PageSection

class FooterForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'  # Incluye todos los campos del modelo Footer

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['name', 'slug', 'description', 'show_in_navbar', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PageSectionForm(forms.ModelForm):
    class Meta:
        model = PageSection
        fields = ['page', 'name', 'row', 'column', 'zone']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class carouselPageForm(forms.ModelForm):
    class Meta:
        model = carouselPage
        fields = ['name', 'imagen', 'details']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
