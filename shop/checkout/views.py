from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Checkout
from cart.cart import Cart
from shop.models import Order, OrderItem, Product
from authentication.models.profiles import Profiles
from authentication.address.models import Address

def checkout_list(request):
    cart = Cart(request)
    products = cart.get_prods()
    quantities = cart.get_quants()
    total = cart.cart_total()

    line_totals = {}
    for product in products:
        qty = int(quantities.get(str(product.id), 0))
        line_totals[product.id] = product.price * qty

    profile = None
    address = None
    profile_missing = False
    address_missing = False
    if request.user.is_authenticated:
        profile = Profiles.objects.filter(user=request.user).first()
        address = Address.objects.filter(user=request.user, address_type="residencial").first()
        profile_missing = not profile
        address_missing = (not address) or (not getattr(address, "street", None))

    checkout_pay_url = reverse('shop:checkout:checkout_pay')
    profile_url = f"{reverse('authentication:profile_create')}?next={checkout_pay_url}"
    login_url = f"{reverse('authentication:login')}?next={checkout_pay_url}"

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
        'quantities': quantities,
        'line_totals': line_totals,
        'total': total,
        'last_order': last_order,
        'profile': profile,
        'address': address,
        'profile_missing': profile_missing,
        'address_missing': address_missing,
        'profile_url': profile_url,
        'checkout_pay_url': checkout_pay_url,
        'login_url': login_url,
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

    return redirect('shop:checkout:checkout_list')


def checkout_pay(request):
    """
    Convert current cart into an Order pending payment and redirect to payments Checkout.
    - Reuse existing pending Order from session if available (idempotent per session)
    """
    if not request.user.is_authenticated:
        request.session["auth_intent"] = {
            "source": "shop",
            "next": reverse('shop:checkout:checkout_pay'),
        }
        return redirect("authentication:register")

    profile = Profiles.objects.filter(user=request.user).first()
    address = Address.objects.filter(user=request.user, address_type="residencial").first()
    if not profile or not address or not getattr(address, "street", None):
        request.session["auth_intent"] = {
            "source": "shop",
            "next": reverse('shop:checkout:checkout_pay'),
        }
        return redirect(f"{reverse('authentication:profile_create')}?next={reverse('shop:checkout:checkout_pay')}")

    cart = Cart(request)
    products = cart.get_prods()
    quantities = cart.get_quants()
    total = cart.cart_total()  # Decimal
    if not products or total <= 0:
        messages.info(request, "Tu carrito está vacío.")
        return redirect('shop:cart_summary')

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
        # Limpiar carrito después de crear la orden
        cart.session['session_key'] = {}
        cart.session.modified = True

    return redirect(reverse('payments:start_order_checkout', kwargs={'order_id': order.id}))
