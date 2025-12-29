from __future__ import annotations

from django import forms

from classroom.courses.models import Course

from .models import InPersonCertificateIssue


class InPersonCertificateIssueForm(forms.ModelForm):
    class Meta:
        model = InPersonCertificateIssue
        fields = ('course', 'issued_date', 'district', 'in_person_total', 'impact', 'quantity', 'image', 'note')
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'issued_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 01-01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'in_person_total': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'impact': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.order_by('title')
