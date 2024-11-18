from django.contrib import admin

# Register your models here.
# blog/admin.py
from .models import blogPost, blogCategory

@admin.register(blogPost)
class blogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('category', 'created_at')

@admin.register(blogCategory)
class blogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
