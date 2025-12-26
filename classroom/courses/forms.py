from django import forms
from .models import Course, Module, Lesson, Test, Question


def _append_css_class(widget, css_class: str) -> None:
    existing = (widget.attrs.get('class') or '').split()
    for c in (css_class or '').split():
        if c and c not in existing:
            existing.append(c)
    widget.attrs['class'] = ' '.join(existing).strip()

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'image', 'published']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')
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

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['module', 'title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['test', 'text', 'option_a', 'option_b']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            _append_css_class(self.fields[field].widget, 'form-control')
        if 'text' in self.fields:
            _append_css_class(self.fields['text'].widget, 'rich-text')
        for name in ['option_a', 'option_b', 'option_c', 'option_d', 'correct_option']:
            if name in self.fields:
                _append_css_class(self.fields[name].widget, 'form-control')
