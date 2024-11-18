# blog/forms.py

from django import forms
from .models import blogPost, blogCategory

class blogCategoryForm(forms.ModelForm):
    class Meta:
        model = blogCategory
        fields = ['name', 'description']

class blogPostForm(forms.ModelForm):
    class Meta:
        model = blogPost
        fields = ['title', 'content', 'category', 'cover_image', 'thumbnail', 'use_thumbnail_as_cover']
