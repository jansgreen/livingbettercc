from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Footer, Column, PageContent, CategoryImages, ImagenPage, pageCategory
from .forms import FooterForm, PageContentForm, ColumnForm, PageContentForm, ImagenPageForm, CategoryImgForm, pageCategoryForm
from django.contrib import messages
from django.shortcuts import render, redirect


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
        print(request.FILES.get('cover_image'))
        if form.is_valid():
            page_content = form.save(commit=False)
            page_content.author = request.user  # Asignar el autor actual
            page_content.save()
            return redirect('page_content_list')  # Cambia 'page_content_list' por la URL a la que deseas redirigir
    else:
        form = PageContentForm()
    
    return render(request, 'create_page_content.html', {'form': form})

@user_passes_test(is_admin_or_editor)
def manage_columns(request):
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_columns')  # Redirige a la misma vista
    else:
        form = ColumnForm()

    columns = Column.objects.all()  # Obtener todas las columnas
    return render(request, 'manage_columns.html', {'form': form, 'columns': columns})

@user_passes_test(is_admin_or_editor)
def edit_column(request, column_id):
    column = Column.objects.get(id=column_id)
    if request.method == 'POST':
        form = ColumnForm(request.POST, instance=column)
        if form.is_valid():
            form.save()
            return redirect('manage_columns')  # Redirigir después de editar
    else:
        form = ColumnForm(instance=column)

    return render(request, 'edit_column.html', {'form': form, 'column': column})

@user_passes_test(is_admin_or_editor)
def delete_column(request, column_id):
    column = Column.objects.get(id=column_id)
    if request.method == 'POST':
        column.delete()
        return redirect('manage_columns')  # Redirigir después de eliminar

    return render(request, 'delete_column.html', {'column': column})

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
            return redirect('page_content_list')  # Redirige a la lista de contenidos de página
    else:
        form = PageContentForm(instance=content)  # Si no es POST, crea un formulario con los datos actuales

    return render(request, 'edit_page_content.html', {'form': form, 'content': content})

@user_passes_test(is_admin_or_editor)
def delete_page_content(request, content_id):
    # Obtiene el contenido de la página o lanza un error 404 si no se encuentra
    content = get_object_or_404(PageContent, id=content_id)

    if request.method == 'POST':
        content.delete()  # Elimina el contenido de la base de datos
        return redirect('page_content_list')  # Redirige a la lista de contenidos de página

    return render(request, 'delete_page_content.html', {'content': content})

@user_passes_test(is_admin_or_editor)
def img_category_list(request):
    forms = ImagenPageForm()
    categories = CategoryImages.objects.all()
    img_list = ImagenPage.objects.all()
    if request.method =="POST":
        forms = ImagenPageForm(request.POST, request.FILES)
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Su imagen se ha subido exitosamente')
        else:
            messages.warning(request, f'{forms.errors}, Fallo la subida de imagen')
    context = {
        'forms': forms,
        'categories': categories,
        'img_list': img_list,
        }
    return render(request, 'img_category_list.html', context)

@user_passes_test(is_admin_or_editor)
def img_category_create(request):
    if request.method == 'POST':
        form = CategoryImgForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('img_category_list')  # Cambia esto según tu URL de listado de habilidades
    else:
        form = CategoryImgForm()
    return render(request, 'page_img_form.html', {'form': form})

@user_passes_test(is_admin_or_editor)
def img_category_update(request, pk):
    page_img = get_object_or_404(CategoryImages, pk=pk)
    if request.method == 'POST':
        form = CategoryImgForm(request.POST, instance=page_img)
        if form.is_valid():
            form.save()
            return redirect('img_category_list')
    else:
        form = CategoryImgForm(instance=page_img)
    return render(request, 'page_img_form.html', {'form': form})

@user_passes_test(is_admin_or_editor)
def img_category_delete(request, pk):
    page_img = get_object_or_404(CategoryImages, pk=pk)
    if request.method == 'POST':
        page_img.delete()
        return redirect('img_category_list')
    return render(request, 'page_img_confirm_delete.html', {'page_img': page_img})

@user_passes_test(is_admin_or_editor)
def imagen_create(request, img_id):
    category = get_object_or_404(CategoryImages, pk=img_id)
    if request.method == 'POST':
        form = ImagenPageForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save(commit=False)
            imagen.category = category
            imagen.save()
            return redirect('img_category_list')
    else:
        form = ImagenPageForm()
    return render(request, 'imagen_form.html', {'form': form, 'habilidad': habilidad})

@user_passes_test(is_admin_or_editor)
def imagen_delete(request, img_id):
    imagen = get_object_or_404(ImagenPage, pk=img_id)
    if request.method == 'POST':
        imagen.delete()
        messages.success(request, 'Se elimino exitosamente')
        return redirect('img_category_list')
    return render(request, 'imagen_confirm_delete.html', {'imagen': imagen})

def crear_columna(request):
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias_y_columnas')  # Cambia la URL de redirección si es necesario
    else:
        form = ColumnForm()
    return render(request, 'crear_columna.html', {'form': form})

def crear_categoria(request):
    if request.method == 'POST':
        form = pageCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias')  # Cambia la URL de redirección si es necesario
    else:
        form = pageCategoryForm()
    return render(request, 'crear_categoria.html', {'form': form})

def listar_categorias_y_columnas(request):
    categorias = pageCategory.objects.prefetch_related('columns').all()
    return render(request, 'listar_categorias_y_columnas.html', {'categorias': categorias})

def delete_columna(request, pk):
    col = Column.objects.get(num=pk)
    col.delete()
    return redirect(listar_categorias_y_columnas)

def delete_pageCategorias(request, pk):
    categorias = pageCategory.objects.get(pk=pk)
    categorias.delete()
    return redirect(listar_categorias_y_columnas)