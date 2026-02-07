from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from urllib3 import request
from authentication.models import address
from .models import Address
from .forms import AddressForm
from django.contrib import messages
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import AddressForm
from .models import Address



# Create your views here.
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'authentication/address_list.html', {'addresses': addresses})

@login_required
def address_detail(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    return render(request, 'authentication/address_detail.html', {'address': address})

def _safe_next_url(request, raw_next: str | None, fallback_name: str = "dashboard") -> str:
    """
    Devuelve un next seguro (misma app/host). Si no es seguro, devuelve fallback.
    """
    if not raw_next:
        return reverse(fallback_name)
    if url_has_allowed_host_and_scheme(raw_next, allowed_hosts={request.get_host()}):
        return raw_next
    return reverse(fallback_name)


@login_required
def address_create(request, address_type, pk):
    """
    Crear/editar dirección del usuario autenticado.
    Flujo recomendado:
    - Si vienes de Profile/Register, te mandan con ?next=...
    - Guardas Address
    - Rediriges al next seguro (ideal: profile_create) para continuar el intent
    """

    # Seguridad: no permitir editar direcciones de otro usuario por URL
    if int(pk) != request.user.id:
        messages.error(request, "No tienes permiso para editar la dirección de otro usuario.")
        return redirect("dashboard")

    # Resolver next: primero GET, pero en POST puede venir en hidden input
    query_next = request.GET.get("next")
    intent = request.session.get("auth_intent") or {}

    # Si no viene next explícito, usamos uno sensato: volver a profile_create
    default_next = reverse("authentication:profile_create")

    raw_next = query_next or intent.get("next") or default_next
    next_url = _safe_next_url(request, raw_next, fallback_name="dashboard")

    address_instance = Address.objects.filter(
        user=request.user,
        address_type=address_type
    ).first()

    if request.method == "POST":
        # Mantener next en POST (si lo envías como hidden en el template)
        post_next = request.POST.get("next")
        if post_next:
            next_url = _safe_next_url(request, post_next, fallback_name="dashboard")

        form = AddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.address_type = address_type
            address.save()

            messages.success(
                request,
                f"Dirección {address.get_address_type_display()} guardada exitosamente."
            )

            # ✅ Regresa al siguiente paso del flujo (normalmente profile_create),
            # donde ya se decide si se consume auth_intent y se manda a classroom/shop/etc.
            return redirect(next_url)

        messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = AddressForm(instance=address_instance)

    context = {
        "form": form,
        "address_type": address_type,
        "address_type_display": dict(Address.a_type).get(address_type, address_type),
        "user_id": request.user.id,
        "next": next_url,  # 👈 para ponerlo como hidden en el template
    }
    return render(request, "direccion.html", context)

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
