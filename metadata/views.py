from django.shortcuts import render, redirect
from .forms import MetaDataForm

from django.shortcuts import render, get_object_or_404, redirect
from .models import MetaData
from .forms import MetaDataForm
from django.contrib import messages

# Vista para crear metadatos
def create_metadata(request):
    if request.method == 'POST':
        form = MetaDataForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Metadatos creados exitosamente.')
            return redirect('metadata_list')  # Cambia por la URL de tu lista de metadatos
    else:
        form = MetaDataForm()
    return render(request, 'create_metadata.html', {'form': form})

def metadata_list(request):
    # Recupera todos los metadatos para mostrarlos en la lista
    metadata_list = MetaData.objects.all()
    return render(request, 'metadata_list.html', {'metadata_list': metadata_list})

def edit_metadata(request, metadata_id):
    # Obtiene el metadato por ID o lanza un error 404 si no existe
    metadata = get_object_or_404(MetaData, id=metadata_id)
    if request.method == 'POST':
        form = MetaDataForm(request.POST, request.FILES, instance=metadata)
        if form.is_valid():
            form.save()
            messages.success(request, 'Metadato actualizado exitosamente.')
            return redirect('metadata_list')
    else:
        form = MetaDataForm(instance=metadata)
    return render(request, 'edit_metadata.html', {'form': form, 'metadata': metadata})

def delete_metadata(request, metadata_id):
    # Obtiene el metadato por ID o lanza un error 404 si no existe
    metadata = get_object_or_404(MetaData, id=metadata_id)
    if request.method == 'POST':
        metadata.delete()
        messages.success(request, 'Metadato eliminado exitosamente.')
        return redirect('metadata_list')
    return render(request, 'confirm_delete_metadata.html', {'metadata': metadata})
