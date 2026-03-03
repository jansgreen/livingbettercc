from django import forms
from .models import Course, Module, Lesson


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'manual_certified_add', 'price', 'image', 'study_material', 'study_material_drive_url', 'published', 'payment_required']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'payment_required':
                _append_css_class(self.fields[field].widget, 'form-check-input')
            if 'published' in self.fields:
                _append_css_class(self.fields['published'].widget, 'form-check-input')
            if 'image' in self.fields:
                _append_css_class(self.fields['image'].widget, 'form-control-file')
            if 'study_material' in self.fields:
                _append_css_class(self.fields['study_material'].widget, 'form-control-file')
            if 'study_material_drive_url' in self.fields:
                _append_css_class(self.fields['study_material_drive_url'].widget, 'form-control')

        self.fields['study_material_drive_url'].label = 'Link del material (Google Drive)'
        self.fields['study_material_drive_url'].help_text = 'Pega el enlace compartido de Google Drive para descarga.'

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'title', 'content', 'video_url', 'video_file', 'order']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

# Removed legacy Test/Question forms; questions now live in quicktest app
