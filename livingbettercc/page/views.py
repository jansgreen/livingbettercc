from django.shortcuts import render, redirect
from .models import Footer
from .forms import FooterForm  # Creamos el formulario más adelante

def ver_footer(request):
    footer = Footer.objects.last()  # Obtener el último registro de Footer
    return render(request, 'ver_footer.html', {'footer': footer})

def agregar_footer(request):
    if request.method == 'POST':
        form = FooterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_footer')  # Redirigir a la vista de visualización
    else:
        form = FooterForm()
    return render(request, 'agregar_footer.html', {'form': form})
