from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Footer, Column, PageContent
from .forms import FooterForm, PageContentForm, ColumnForm, PageContentForm

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
        form = PageContentForm(request.POST)
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
