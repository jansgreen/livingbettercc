from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address
from .forms import AddressForm

# Create your views here.
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'authentication/address_list.html', {'addresses': addresses})

@login_required
def address_detail(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    return render(request, 'authentication/address_detail.html', {'address': address})

@login_required
def address_create(request, address_type, pk):
    """
        Esta funcion actua como un core en direccion, primero se creara el usuario y luego viene redirijido aqui para crear su direccion
        desde la funcion de origen enviara el tipo de direccion, el grupo de accesso y el id de usuario.
    """
    # Obtener dirección existente si existe
    address_instance = Address.objects.filter(user__id=pk, address_type=address_type).first()

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            address = form.save(commit=False)
            # Vincular al usuario indicado por pk (ya debería estar autenticado)
            address.user_id = pk
            address.address_type = address_type
            address.save()
            messages.success(request, f'Dirección {address.get_address_type_display()} guardada exitosamente.')
            # Redirigir según el contexto (puede personalizarse)
            next_url = request.GET.get('next', 'authentication:login')
            return redirect(next_url)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AddressForm(instance=address_instance)

    context = {
        'form': form,
        'address_type': address_type,
        'address_type_display': dict(Address.a_type).get(address_type, address_type),
        'user_id': pk,
    }
    return render(request, 'direccion.html', context)
@login_required
def address_update(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('authentication:address:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'authentication/address_form.html', {'form': form})

@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('authentication:address:address_list')
    return render(request, 'authentication/address_confirm_delete.html', {'address': address})
