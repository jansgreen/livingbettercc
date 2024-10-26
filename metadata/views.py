from django.shortcuts import render, redirect
from .forms import MetaDataForm

def create_metadata(request):
    if request.method == 'POST':
        form = MetaDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('metadata_success')  # Redirige a una página de éxito
    else:
        form = MetaDataForm()
    return render(request, 'create_metadata.html', {'form': form})
