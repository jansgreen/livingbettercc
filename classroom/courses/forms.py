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
        fields = ['title', 'description', 'manual_certified_add', 'price', 'image', 'published', 'payment_required']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'payment_required':
                _append_css_class(self.fields[field].widget, 'form-check-input')
            if 'published' in self.fields:
                _append_css_class(self.fields['published'].widget, 'form-check-input')
            if 'image' in self.fields:
                _append_css_class(self.fields['image'].widget, 'form-control-file')

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
        fields = ['module', 'title', 'content', 'video_url', 'order']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

# Removed legacy Test/Question forms; questions now live in quicktest app
