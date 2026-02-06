from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem, Category, SubCategory
from .forms import ProductForm, CategoryForm, SubCategoryForm
from django.conf import settings
from classroom.courses.models import Course
import requests
from django.contrib import messages
from cart.cart import Cart as sc  # Import Cart with alias sc
from django.utils.text import slugify
from django.db import IntegrityError

from django.core.paginator import Paginator

def product_list(request):
    # Búsqueda
    search_query = request.GET.get('q', '').strip()

    courses = Course.objects.all()
    products = Product.objects.all()

    if search_query:
        courses = courses.filter(title__icontains=search_query)
        products = products.filter(title__icontains=search_query)

    # Paginación
    course_paginator = Paginator(courses, 8)
    product_paginator = Paginator(products, 8)
    course_page_number = request.GET.get('course_page')
    product_page_number = request.GET.get('product_page')
    course_page_obj = course_paginator.get_page(course_page_number)
    product_page_obj = product_paginator.get_page(product_page_number)

    context = {
        'courses': course_page_obj,
        'products': product_page_obj,
        'search_query': search_query,
    }
    return render(request, 'product_list.html', context)

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop:product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shop:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('shop:product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'product_detail.html', context)

# List categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_Shop_list.html', {'categories': categories})

#Create category
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

# View to add a product to the cart
def cart_add(request, product_id, product_qty):
    cart = sc(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product_id=product_id, product_qty=product_qty)
    messages.success(request, f"{product.name} added to cart.")
    return redirect('shop:product_list')

# View to remove a product from the cart
def cart_delete(request, product_id):
    cart = sc(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"{product.name} removed from cart.")
    return redirect('shop:cart_summary')

# View to display cart details
def cart_summary(request):
    cart = sc(request)
    products = cart.get_prods()
    quantities = cart.get_quants()
    total = cart.cart_total()
    line_totals = {}
    for product in products:
        qty = int(quantities.get(str(product.id), 0))
        line_totals[product.id] = product.price * qty
    context = {
        'cart': cart,
        'products': products,
        'quantities': quantities,
        'line_totals': line_totals,
        'total': total,
    }
    return render(request, 'cart.html', context)

# View to clear the cart
def clear_cart(request):
    cart = sc(request)
    cart.clear()
    messages.success(request, "Cart cleared.")
    return redirect('shop:product_list')

# View to update the quantity of a product in the cart
def cart_update(request, product_id):
    cart = sc(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = request.POST.get('quantity', 1)
    try:
        quantity = int(quantity)
        if quantity > 0:
            cart.add(product=product, quantity=quantity, update_quantity=True)
            messages.success(request, f"Updated {product.name} quantity to {quantity}.")
        else:
            messages.error(request, "Quantity must be greater than zero.")
    except ValueError:
        messages.error(request, "Invalid quantity.")
    return redirect('shop:cart_summary')

# View to create a subcategory
def subcategory_create(request, category_id):
    category = Category.objects.get(pk=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')

        # Generate a unique slug if not provided or if duplicate
        if not slug:
            slug = slugify(name)
        original_slug = slug
        counter = 1
        while SubCategory.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        try:
            subcategory = SubCategory(name=name, slug=slug, description=description, category=category)
            subcategory.save()
            return redirect('category_list')
        except IntegrityError:
            return render(request, 'subcategory_form.html', {
                'error': 'Error creating subcategory. Please check the form.',
                'category': category,
            })
    return redirect('category_list')

def thanks(request):
    return render(request, 'thanks.html')

@login_required
def order_detail(request, order_id: int):
    from shop.models import Order
    order = get_object_or_404(Order, id=order_id)
    if not (request.user.is_staff or order.user_id == request.user.id):
        return redirect('shop:product_list')

    items = order.items.select_related('product').all()
    item_lines = []
    for item in items:
        line_total_cents = item.qty * item.unit_price_cents
        item_lines.append({
            "item": item,
            "unit_price": item.unit_price_cents / 100,
            "line_total": line_total_cents / 100,
        })
    receipt = None
    try:
        from payments.models import Payment
        p = (
            Payment.objects.filter(
                purpose=Payment.PURPOSE_SHOP_ORDER,
                reference_id=str(order.id),
                status=Payment.STATUS_PAID,
            )
            .order_by('-created_at')
            .first()
        )
        if p and hasattr(p, 'receipt'):
            receipt = p.receipt
    except Exception:
        pass

    ctx = {
        'order': order,
        'items': items,
        'item_lines': item_lines,
        'total_amount': order.total_cents / 100,
        'receipt': receipt,
    }
    return render(request, 'shop/order_detail.html', ctx)

def order_return(request):
    """Landing page after successful payment; link to last order if available."""
    order_id = request.session.get('last_order_id')
    has_order = bool(order_id)
    from django.urls import reverse
    fallback_url = reverse('shop:product_list')
    return render(request, 'shop/order_return.html', {
        'order_id': order_id,
        'has_order': has_order,
        'fallback_url': fallback_url,
    })


def order_cancel(request):
    """Landing page after cancelled payment; link to resume payment or view order."""
    order_id = request.session.get('last_order_id')
    has_order = bool(order_id)
    from django.urls import reverse
    fallback_url = reverse('shop:product_list')
    return render(request, 'shop/order_cancel.html', {
        'order_id': order_id,
        'has_order': has_order,
        'fallback_url': fallback_url,
    })
