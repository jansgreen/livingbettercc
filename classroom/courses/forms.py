from django import forms
from .models import Course, Module, Lesson, Test, Question

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'image', 'published']
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields['image'].widget.attrs.update({'class': 'form-control-file'})

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['module', 'title', 'content', 'video_url', 'order']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['module', 'title']
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['test', 'text', 'option_a', 'option_b']
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields['text'].widget.attrs.update({'class': 'form-control rich-text'})
            self.fields['option_a'].widget.attrs.update({'class': 'form-control'})
            self.fields['option_b'].widget.attrs.update({'class': 'form-control'})
            self.fields['option_c'].widget.attrs.update({'class': 'form-control'})
            self.fields['option_d'].widget.attrs.update({'class': 'form-control'})
            self.fields['correct_option'].widget.attrs.update({'class': 'form-control'})
