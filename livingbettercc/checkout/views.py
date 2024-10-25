from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import paypalrestsdk
from django.conf import settings
from catalog.models import Carrito
from .models import Orden 


@login_required
def confirmacion_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET})
    return render(request, 'confirmacion.html', {'orden': orden})

@login_required
def checkout(request):
    carrito = Carrito.objects.get(usuario=request.user)
    total = sum(item.cantidad * item.producto.precio for item in carrito.itemcarrito_set.all())

    if request.method == 'POST':
        direccion_envio = request.POST.get('direccion_envio')

        # Crear el pago en PayPal
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/confirmar_pago/'),
                "cancel_url": request.build_absolute_uri('/cancelar_pago/')
            },
            "transactions": [{
                "amount": {
                    "total": str(total),
                    "currency": "USD"
                },
                "description": "Compra en la tienda"
            }]
        })

        if payment.create():
            print("Payment created successfully")
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)  # Redirige a PayPal para que el usuario complete el pago
        else:
            print(payment.error)  # Maneja el error si ocurre

    return render(request, 'checkout.html', {'carrito': carrito, 'total': total})

@login_required
def confirmar_pago(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Crear la orden en tu base de datos
        direccion_envio = "direccion de ejemplo"  # Debes obtener esto del formulario de checkout
        orden = Orden.objects.create(usuario=request.user, total=payment.transactions[0].amount.total, direccion_envio=direccion_envio)
        
        # Aquí puedes vaciar el carrito o manejarlo como prefieras
        return render(request, 'confirmacion.html', {'orden': orden})
    else:
        return redirect('cancelar_pago')

@login_required
def cancelar_pago(request):
    # Manejar el caso en que el usuario cancela el pago
    return render(request, 'cancelacion.html')


