from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Checkout
from cart.cart import Cart
from shop.models import Order, OrderItem, Product

def checkout_list(request):
    cart = Cart(request)
    products = cart.get_prods()
    quantitie = cart.get_quants()
    total = cart.cart_total()

    for product_id_str, quantities in quantitie.items():
        pass

    # If a recent order exists in session, fetch to enable optional actions
    last_order = None
    last_order_id = request.session.get('last_order_id')
    if last_order_id:
        try:
            from shop.models import Order
            last_order = Order.objects.filter(id=last_order_id).first()
        except Exception:
            last_order = None

    context = {
        'products': products,
        'quantities': quantitie,
        'total': total,
        'last_order': last_order,
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


@login_required
def checkout_pay(request):
    """
    Convert current cart into an Order pending payment and redirect to payments Checkout.
    - Reuse existing pending Order from session if available (idempotent per session)
    """
    cart = Cart(request)
    products = cart.get_prods()
    quantities = cart.get_quants()
    total = cart.cart_total()  # Decimal

    # Reuse a pending order if present in session and belongs to the user
    order = None
    last_order_id = request.session.get('last_order_id')
    if last_order_id:
        order = Order.objects.filter(id=last_order_id, user=request.user, status=Order.Status.PENDING_PAYMENT).first()

    if order is None:
        order = Order.objects.create(
            user=request.user,
            status=Order.Status.PENDING_PAYMENT,
            total_cents=int((total * Decimal('100')).to_integral_value())
        )
        for product in products:
            qty = int(quantities.get(str(product.id), 1))
            OrderItem.objects.create(
                order=order,
                product=product,
                qty=qty,
                unit_price_cents=int((product.price * Decimal('100')).to_integral_value()),
            )
        request.session['last_order_id'] = order.id

    return redirect(reverse('payments:start_order_checkout', kwargs={'order_id': order.id}))
