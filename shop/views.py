from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Cart, CartItem, Order, Category
from .forms import ProductForm, OrderForm, CategoryForm

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

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(id=request.session.get('cart_id'))
    request.session['cart_id'] = cart.id
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('product_list')

def view_cart(request):
    cart = None
    cart_items = []
    if 'cart_id' in request.session:
        cart = get_object_or_404(Cart, id=request.session['cart_id'])
        cart_items = cart.items.all()
    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items})

from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart
from .forms import OrderForm

def checkout(request):
    # Verificar si el carrito existe en la sesión
    cart_id = request.session.get('cart_id')
    print(cart_id)
    if not cart_id:
        # Manejo si no existe carrito en la sesión
        return redirect('view_cart')  # Redirigir al carrito si no se encuentra

    # Obtener el carrito asociado al ID en la sesión
    cart = get_object_or_404(Cart, id=cart_id)

    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        # Guardar información del carrito en la sesión para usar después del login
        request.session['cart_items'] = [item.id for item in cart.items.all()]
        return redirect('signin')  # Cambia 'signin' por el nombre de tu vista de inicio de sesión

    # Manejar el formulario de pedido
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.cart = cart
            order.user = request.user  # Asociar el pedido con el usuario autenticado
            order.save()
            # Limpiar el carrito de la sesión
            del request.session['id']  # Eliminar el carrito de la sesión
            return redirect('product_list')  # Cambia 'product_list' por la vista correspondiente
    else:
        form = OrderForm()

    # Renderizar la página de checkout
    return render(request, 'checkout.html', {'form': form, 'cart': cart})

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
