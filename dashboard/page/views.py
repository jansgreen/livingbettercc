from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Footer, PagePosition, PageContent, PageCategory, carouselPage
from .forms import FooterForm, PageContentForm, PagePositionForm, PageContentForm, PageCategoryForm, carouselPageForm
from django.contrib import messages


def is_admin_or_editor(user):
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'Editor']).exists()

def ver_footer(request):
    footer = Footer.objects.last()  # Obtener el último registro de Footer
    return render(request, 'ver_footer.html', {'footer': footer})

@user_passes_test(is_admin_or_editor)
def agregar_footer(request):
    if request.method == 'POST':
        form = FooterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_footer')  # Redirigir a la vista de visualización
    else:
        form = FooterForm()
    return render(request, 'agregar_footer.html', {'form': form})

@user_passes_test(is_admin_or_editor)
def create_page_content(request):
    if request.method == 'POST':
        form = PageContentForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            page_content = form.save(commit=False)
            page_content.author = request.user  # Asignar el autor actual
            page_content.save()
            return redirect('page:page_content_list')  # Cambia 'page_content_list' por la URL a la que deseas redirigir
    else:
        form = PageContentForm()
    
    return render(request, 'create_page_content.html', {'form': form})

@user_passes_test(is_admin_or_editor)
def manage_PagePosition(request):
    if request.method == 'POST':
        form = PagePositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('page:manage_PagePositions')  # Redirige a la misma vista
    else:
        form = PagePositionForm()

    PagePositions = PagePosition.objects.all()  # Obtener todas las PagePositionas
    return render(request, 'manage_PagePositions.html', {'form': form, 'PagePositions': PagePositions})

@user_passes_test(is_admin_or_editor)
def edit_PagePosition(request, PagePosition_id):
    PagePosition = PagePosition.objects.get(id=PagePosition_id)
    if request.method == 'POST':
        form = PagePositionForm(request.POST, instance=PagePosition)
        if form.is_valid():
            form.save()
            return redirect('manage_PagePositions')  # Redirigir después de editar
    else:
        form = PagePositionForm(instance=PagePosition)

    return render(request, 'edit_PagePosition.html', {'form': form, 'PagePosition': PagePosition})

@user_passes_test(is_admin_or_editor)
def delete_PagePosition(request, PagePosition_id):
    PagePosition = PagePosition.objects.get(id=PagePosition_id)
    if request.method == 'POST':
        PagePosition.delete()
        return redirect('page:manage_PagePositions')  # Redirigir después de eliminar

    return render(request, 'delete_PagePosition.html', {'PagePosition': PagePosition})

@user_passes_test(is_admin_or_editor)
def manage_page_content(request):
    page_contents = PageContent.objects.all()  # Obtener todos los contenidos de la página
    return render(request, 'manage_page_content.html', {'page_contents': page_contents})

@user_passes_test(is_admin_or_editor)
def page_content_list(request):
    page_contents = PageContent.objects.all()  # Obtener todos los contenidos de la página
    return render(request, 'page_content_list.html', {'page_contents': page_contents})

@user_passes_test(is_admin_or_editor)
def edit_page_content(request, content_id):
    # Obtiene el contenido de la página o lanza un error 404 si no se encuentra
    content = get_object_or_404(PageContent, id=content_id)

    if request.method == 'POST':
        # Si la solicitud es POST, intenta guardar los datos del formulario
        form = PageContentForm(request.POST, instance=content)  # Vincula el formulario a la instancia existente
        if form.is_valid():
            form.save()  # Guarda los cambios
            return redirect('page:page_content_list')  # Redirige a la lista de contenidos de página
    else:
        form = PageContentForm(instance=content)  # Si no es POST, crea un formulario con los datos actuales

    return render(request, 'edit_page_content.html', {'form': form, 'content': content})

@user_passes_test(is_admin_or_editor)
def delete_page_content(request, content_id):
    # Obtiene el contenido de la página o lanza un error 404 si no se encuentra
    content = get_object_or_404(PageContent, id=content_id)

    if request.method == 'POST':
        content.delete()  # Elimina el contenido de la base de datos
        return redirect('page:page_content_list')  # Redirige a la lista de contenidos de página

    return render(request, 'delete_page_content.html', {'content': content})

def crear_PagePosition(request):
    if request.method == 'POST':
        form = PagePositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('page:listar_categorias_y_PagePosition')  # Cambia la URL de redirección si es necesario
    else:
        form = PagePositionForm()
    return render(request, 'crear_PagePosition.html', {'form': form})

def crear_PageCategory(request):
    if request.method == 'POST':
        form = PageCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('page:listar_categorias_y_PagePosition')  # Cambia la URL de redirección si es necesario
    else:
        form = PageCategoryForm()
    return render(request, 'crear_PageCategory.html', {'form': form})

def listar_categorias_y_PagePosition(request):
    categorias = PageCategory.objects.all()
    return render(request, 'listar_categorias_y_PagePosition.html', {'categorias': categorias})

def delete_PagePosition(request, pk):
    col = PagePosition.objects.get(num=pk)
    col.delete()
    return redirect('page:listar_categorias_y_PagePosition')

def delete_pageCategorias(request, pk):
    categorias = PageCategory.objects.get(pk=pk)
    categorias.delete()
    return redirect('page:listar_categorias_y_PagePosition')

def carouselPageFunction(request):
    if request.method == "POST":
        form = carouselPageForm(request.POST, request.FILES)
        if form.is_valid:
            form.save()
        return redirect('page:carouselPageFunction')
    form = carouselPageForm()
    image = carouselPage.objects.all()
    context = {
        'form':form,
        'image': image,
    }
    return render(request, 'img_list.html', context)

def imagen_delete(request, img_id):
    image = carouselPage.objects.get(id=img_id)
    image.delete()
    return redirect(carouselPageFunction)