from django.shortcuts import render, redirect, get_object_or_404
from .models import Image
from .forms import ImageForm

# Lista de Imágenes
def image_list(request):
    images = Image.objects.all()
    return render(request, 'image_list.html', {'images': images})

# Crear Imagen
def image_create(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('image_list')
    else:
        form = ImageForm()
    return render(request, 'image_form.html', {'form': form})

# Actualizar Imagen
def image_update(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('image_list')
    else:
        form = ImageForm(instance=image)
    return render(request, 'image_form.html', {'form': form, 'image': image})

# Eliminar Imagen
def image_delete(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.method == 'POST':
        image.delete()
        return redirect('image_list')
    return render(request, 'image_confirm_delete.html', {'image': image})
