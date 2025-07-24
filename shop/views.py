from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Product, Cart, CartItem, Category, SubCategory
from .forms import ProductForm, CategoryForm, SubCategoryForm
from django.conf import settings
from classroom.courses.models import Course
import requests
from django.contrib import messages
from cart.cart import Cart as sc  # Import Cart with alias sc
from django.utils.text import slugify
from django.db import IntegrityError

def product_list(request):
    products = Product.objects.all()
    course = Course.objects.all()
    t = [t for t in course ]
    print(t)
    context = {
        'products': products,
        'courses': course,
    }
    return render(request, 'product_list.html', context)

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
    return redirect('product_list')

# View to remove a product from the cart
def cart_delete(request, product_id):
    cart = sc(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f"{product.name} removed from cart.")
    return redirect('cart_summary')

# View to display cart details
def cart_summary(request):
    cart = sc(request)
    return render(request, 'cart.html', {'cart': cart})

# View to clear the cart
def clear_cart(request):
    cart = sc(request)
    cart.clear()
    messages.success(request, "Cart cleared.")
    return redirect('product_list')

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
    return redirect('cart_summary')

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