from django.shortcuts import render, get_object_or_404, redirect
from .models import Checkout
from cart.cart import Cart

def checkout_list(request):
    cart = Cart(request)
    products = cart.get_prods()
    quantitie = cart.get_quants()
    total = cart.cart_total()

    for product_id_str, quantities in quantitie.items():
        pass

    context = {
        'products': products,
        'quantities': quantitie,
        'total': total,
    }
    return render(request, 'checkout/checkout_list.html', context)

def checkout_create(request):
    cart = Cart(request)
    products = cart.get_prods()
    quantities = cart.get_quants()

    for product in products:
        quantity = quantities[str(product.id)]
        total_price = product.price * quantity
        Checkout.objects.create(product=product, quantity=quantity, total_price=total_price)

    return redirect('checkout_list')
