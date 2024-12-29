from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Product, Cart, CartItem, Category
from .forms import ProductForm, CategoryForm
from .models import Cart
from django.conf import settings
from payment.models import Order
import requests
from django.contrib import messages
from cart.cart import Cart as sc  # Import Cart with alias sc




def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

# List categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_Shop_list.html', {'categories': categories})

# Create category
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_Shop_form.html', {'form': form})

# Update category
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form})

# Delete category
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})

def process_cardnet_payment(request, order_id):
    """
    Procesa un pago con la API de CardNet.
    """
    if request.method == "POST":
        # Obtén la orden
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Orden no encontrada."}, status=404)

        # Información de la API (deberás actualizar esto según la documentación de CardNet)
        url = "https://api.cardnet.com.do/transaction"  # Actualiza con la URL real
        headers = {
            "Authorization": f"Bearer {settings.CARDNET_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "amount": str(order.total_amount),
            "currency": "DOP",  # Cambiar si usas otra moneda
            "order_id": str(order.id),
            "description": f"Pago por orden {order.id}",
            "customer": {
                "name": order.customer.name,
                "email": order.customer.email,
                "phone": order.customer.phone,
            },
            "redirect_url": request.build_absolute_uri("/shop/payment-confirmation/"),
        }

        try:
            # Envía la solicitud a la API de CardNet
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                # Marca la orden como pagada
                order.payment_status = "PAID"
                order.transaction_id = response_data.get("transaction_id")
                order.save()

                return JsonResponse({
                    "message": "Pago procesado con éxito.",
                    "transaction_id": response_data.get("transaction_id"),
                })
            else:
                return JsonResponse({
                    "error": "No se pudo procesar el pago.",
                    "details": response_data,
                }, status=400)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Error de conexión con CardNet.", "details": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido."}, status=405)


# Cart
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Product
from cart.cart import Cart as sc  # Import Cart with alias sc

def cart_summary(request):
    # Get the cart
    cart = sc(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals})

def cart_add(request):
    # Get the cart
    cart = sc(request)
    # test for POST
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        # lookup product in DB
        product = get_object_or_404(Product, id=product_id)
    
        # Save to session
        cart.add(product_id, product_qty)

        # Get Cart Quantity
        cart_quantity = len(cart)

        # Return response
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, "Product Added To Cart...")
        return response

def cart_delete(request):
    cart = sc(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        # Call delete Function in Cart
        cart.delete(product=product_id)

        response = JsonResponse({'product': product_id})
        messages.success(request, "Item Deleted From Shopping Cart...")
        return response

def cart_update(request):
    cart = sc(request)
    if request.POST.get('action') == 'post':
        # Get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty': product_qty})
        messages.success(request, "Your Cart Has Been Updated...")
        return response

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(id=request.session.get('cart_id'))
    request.session['cart_id'] = cart.id
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('product_list')
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(id=request.session.get('cart_id'))
    request.session['cart_id'] = cart.id
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('product_list')