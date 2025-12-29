from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import ContentCategory, ContentPost
from .forms import ContentCategoryForm, ContentPostForm

# Create your views here.

def ContentListView(request):
    contents = ContentPost.objects.all()
    context = {'contents': contents}
    return render(request, 'contents/content_list.html', context)

def ContentDetailView(request, pk):
    content = get_object_or_404(ContentPost, pk=pk)
    # Prepare tags as a list for template iteration (templates cannot call split())
    tags_list = []
    if getattr(content, 'tags', None):
        # split by comma and strip whitespace
        tags_list = [t.strip() for t in content.tags.split(',') if t.strip()]

    # Optionally provide related contents (same category), used by the template if available
    related_contents = []
    if getattr(content, 'category', None):
        related_contents = ContentPost.objects.filter(category=content.category).exclude(pk=content.pk)[:3]

    context = {'content': content, 'tags_list': tags_list, 'related_contents': related_contents}
    return render(request, 'contents/content_detail.html', context)

def ContentCreateView(request):
    if request.method == "POST":
        form = ContentPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Contenido creado exitosamente.")
            return redirect('contents:ContentListView')
        else:
            messages.error(request, f'{form.errors}Error al crear el contenido. Por favor, verifica los datos ingresados.')
    else:
        form = ContentPostForm()
    return render(request, 'contents/content_form.html', {'form': form})

def ContentUpdateView(request, pk):
    content = get_object_or_404(ContentPost, pk=pk)
    if request.method == "POST":
        form = ContentPostForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Contenido actualizado exitosamente.")
            # After updating content, return to the content list (was incorrectly pointing to CategoryListView)
            return redirect('contents:ContentListView')
        else:
            messages.error(request, f'{form.errors}Error al actualizar el contenido. Por favor, verifica los datos ingresados.')
    else:
        form = ContentPostForm(instance=content)
    return render(request, 'contents/content_form.html', {'form': form})

def ContentDeleteView(request, pk):
    content = get_object_or_404(ContentPost, pk=pk)
    if request.method == "POST":
        content.delete()
        messages.success(request, "Contenido eliminado exitosamente.")
        # After deleting content, return to the content list
        return redirect('contents:ContentListView')
    return render(request, 'contents/content_confirm_delete.html', {'content': content})

# CRUD para Categorías de Contenido
def CategoryListView(request):
    categories = ContentCategory.objects.all()
    context = {'categories': categories}
    return render(request, 'contents/category_list.html', context)

def CategoryCreateView(request):
    if request.method == "POST":
        form = ContentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría creada exitosamente.")
            return redirect('contents:CategoryListView')
        else:
            messages.error(request, f'{form.errors}Error al crear la categoría. Por favor, verifica los datos ingresados.')
    else:
        form = ContentCategoryForm()
    context = {'form': form}
    return render(request, 'contents/category_form.html', context)

def CategoryUpdateView(request, pk):
    category = get_object_or_404(ContentCategory, pk=pk)
    if request.method == "POST":
        form = ContentCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría actualizada exitosamente.")
            return redirect('contents:CategoryListView')
        else:
            messages.error(request, f'{form.errors}Error al actualizar la categoría. Por favor, verifica los datos ingresados.')
    else:
        form = ContentCategoryForm(instance=category)
    context = {'form': form}
    return render(request, 'dashboard/contents/category_form.html', context)

def CategoryDeleteView(request, pk):
    category = get_object_or_404(ContentCategory, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Categoría eliminada exitosamente.")
        return redirect('contents:CategoryListView')
    return render(request, 'contents/category_confirm_delete.html', {'category': category})
