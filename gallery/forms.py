from django import forms
from .models import Image

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'description', 'image_file', 'forcarousel']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply a consistent `form-control` class to all visible fields
        for field_name, field in self.fields.items():
            if field_name == "forcarousel":
                field.widget.attrs.update({'class': 'form-check-input', 'id':"exampleCheck1", 'type': 'checkbox'})
            else:
                field.widget.attrs.update({'class': 'form-control'})