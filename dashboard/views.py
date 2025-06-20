from django.shortcuts import render, redirect, get_object_or_404
from dashboard.models import CategoriaMenu, MenuItem
from dashboard.forms import CategoriaMenuForm, MenuItemForm

def dashboards(request):
    # Ensure the correct template path and context are used
    return render(request, 'dashboard.html')  # Correct template path

def menu(request):
         
    return render(request, 'dashboard/menu/menu.html')  # Correct template path

def categoria_menu_list(request):
    categorias = CategoriaMenu.objects.all()
    return render(request, 'dashboard/menu/categoria_menu_list.html', {'categorias': categorias})

def categoria_menu_create(request):
    if request.method == 'POST':
        form = CategoriaMenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoria_menu_list')
    else:
        form = CategoriaMenuForm()
    return render(request, 'dashboard/menu/categoria_menu_form.html', {'form': form})

def categoria_menu_update(request, pk):
    categoria = get_object_or_404(CategoriaMenu, pk=pk)
    if request.method == 'POST':
        form = CategoriaMenuForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoria_menu_list')
    else:
        form = CategoriaMenuForm(instance=categoria)
    return render(request, 'dashboard/menu/categoria_menu_form.html', {'form': form})

def categoria_menu_delete(request, pk):
    categoria = get_object_or_404(CategoriaMenu, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('categoria_menu_list')
    return render(request, 'dashboard/menu/categoria_menu_confirm_delete.html', {'categoria': categoria})

def menuitem_list(request):
    items = MenuItem.objects.all()
    return render(request, 'dashboard/menu/menuitem_list.html', {'items': items})

def menuitem_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menuitem_list')
    else:
        form = MenuItemForm()
    return render(request, 'dashboard/menu/menuitem_form.html', {'form': form})

def menuitem_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('menuitem_list')
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'dashboard/menu/menuitem_form.html', {'form': form})

def menuitem_delete(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('menuitem_list')
    return render(request, 'dashboard/menu/menuitem_confirm_delete.html', {'item': item})

