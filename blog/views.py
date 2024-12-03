
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import blogPost, blogCategory
from .forms import blogPostForm, blogCategoryForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Count
from gallery.models import Image

def blog(request):
    form = blogPost.objects.all()
    # Obtener los años y meses de los posts
    archives = blogPost.objects.annotate(year=Count('created_at__year'), month=Count('created_at__month')) \
        .values('created_at__year', 'created_at__month') \
        .order_by('-created_at__year', '-created_at__month')
    
    context = {
        'form': form, 
        'archives': archives

    }

    return render(request, 'blog_index.html', context)

def post_list(request):
    posts = blogPost.objects.all()
    return render(request, 'post_list.html', {'posts': posts})

def post_create(request):
    if request.method == 'POST':
        form = blogPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = blogPostForm()
    return render(request, 'post_form.html', {'form': form})

def post_update(request, pk):
    post = get_object_or_404(blogPost, pk=pk)
    if request.method == 'POST':
        form =blogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = blogPostForm(instance=post)
    gallery_images = Image.objects.all()  # Obtener todas las imágenes de la galería
    return render(request, 'post_form.html', {'form': form, 'gallery_images':gallery_images})

def post_detail(request, pk):
    post = get_object_or_404(blogPost, pk=pk)
    return render(request, 'post_detail.html', {'post': post})

def post_delete(request, pk):
    post = get_object_or_404(blogPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'post_confirm_delete.html', {'post': post})

class CategoryListView(ListView):
    model = blogCategory
    template_name = 'category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(CreateView):
    model = blogCategory
    form_class = blogCategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryUpdateView(UpdateView):
    model = blogCategory
    form_class = blogCategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(DeleteView):
    model = blogCategory
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

def archive_posts(request, year, month):
    posts = blogPost.objects.filter(created_at__year=year, created_at__month=month)
    return render(request, 'index.html', {'posts': posts, 'year': year, 'month': month})