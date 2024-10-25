from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, CategoriaProducto, ProductImage, Carrito, ItemCarrito
from .forms import ProductoForm, CategoriaProductoForm, ProductImageForm
from django.contrib.auth.decorators import login_required


def listar_categorias(request):
    categorias = CategoriaProducto.objects.all()
    return render(request, 'listar_categorias.html', {'categorias': categorias})

def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_categorias')
    else:
        form = CategoriaProductoForm()
    return render(request, 'crear_categoria.html', {'form': form})

def lista_productos(request):
    # Obtén el carrito, pero verifica si el usuario está autenticado
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        # Si el usuario no está autenticado, puedes asignar None o un carrito vacío
        carrito = None  # O podrías usar Carrito() para un carrito vacío sin usuario

    productos = Producto.objects.all()

    if productos:
        # Aquí podrías incluir alguna lógica para el carrito si hay productos
        pass
    else:
        # Aquí podrías agregar un mensaje para indicar que no hay productos
        context = {
            'mensaje': 'No hay productos disponibles.',
        }

    context = {
        'carrito': carrito,
        'productos': productos,
    }

    return render(request, 'lista_productos.html', context)

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'detalle_producto.html', {'producto': producto})

def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        image_form = ProductImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        if form.is_valid():
            product = form.save()
                        # Verifica cuántas imágenes tiene el producto antes de guardar
            if len(files) + product.images.count() > 5:
                form.add_error(None, "No puedes subir más de 5 imágenes para este producto.")
            else:
                for file in files:
                    ProductImage.objects.create(product=product, image=file)
            return redirect('lista_productos')
    else:
        form = ProductoForm()
        image_form = ProductImageForm()
    return render(request, 'crear_producto.html', {'form': form, 'image_form': image_form})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'form': form})

def eliminar_producto(request, pk):
    producto = Producto.objects.get(pk=pk)
    producto.delete()
    return redirect('lista_productos')

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)

    # Obtiene o crea el item en el carrito
    item_carrito, item_created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)

    if item_created:
        # Si el item es creado, establece la cantidad en 1
        item_carrito.cantidad = 1
    else:
        # Si el item ya existe, incrementa la cantidad
        item_carrito.cantidad += 1

    # Guarda el item del carrito
    item_carrito.save()

    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)  # Obtén el carrito del usuario
    items_carrito = carrito.itemcarrito_set.all()  # Obtiene todos los items del carrito

    return render(request, 'carrito.html', {'carrito': carrito, 'items': items_carrito})

@login_required
def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad'))
        carrito = Carrito.objects.get(usuario=request.user)
        item_carrito = get_object_or_404(ItemCarrito, id=item_id)

        if nueva_cantidad > 0:
            item_carrito.cantidad = nueva_cantidad
            item_carrito.save()
        else:
            # Si la cantidad es 0, eliminamos el item del carrito
            item_carrito.delete()

    return redirect('ver_carrito')

@login_required
def eliminar_del_carrito(request, pk):
    carrito = Carrito.objects.get(usuario=request.user)
    
    # Obtiene el item del carrito que corresponde al producto
    item_carrito = ItemCarrito.objects.filter(carrito=carrito, producto__id=pk).first()
    
    if item_carrito:
        item_carrito.delete()  # Elimina el item del carrito
    
    return redirect('ver_carrito')  # Redirige a la página del carrito después de eliminar


