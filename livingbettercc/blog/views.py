from django.contrib import messages

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Categoria, Posicion
from .forms import PostForm, CategoriaForm, PosicionForm

import traceback

def crear_post_Bio(request):
        categorias, catCreada = Categoria.objects.get_or_create(nombre="Biografia")
        num = 1
        while Posicion.objects.filter(nombre=f'biografia-{num}').exists():
            num += 1
        position, posCreada = Posicion.objects.get_or_create(nombre=f'biografia-{num}')
        form = PostForm()
        context = {
            'form':form,
            'Uposition': position.nombre,
            'UpositionId': position.id,
            'Ucategorias':categorias.nombre,
            'UcategoriasId':categorias.id,
            'posCreada': posCreada,
            'catCreada': catCreada,
            }
        return render(request, 'crear_post.html', context)

# elimina y actualiza posicion
def actualizar_posicion(request, pk):
    if pk:
        posicion = get_object_or_404(Posicion, pk=pk)
    else:
        posicion = None
    if request.method == 'POST':
        if 'editar' in request.POST:
            numero = request.POST.get('actualizar')
            nuevo_nombre = f'column-{numero}'
            
            # Verificar si el nombre ya existe
            if Posicion.objects.filter(nombre=nuevo_nombre).exists():
                messages.info(request, 'Esta posición ya existe')
            else:
                posicion.nombre = nuevo_nombre
                posicion.save()  # Guardar el objeto directamente
                messages.info(request, 'Fue actualizado exitosamente')
                return redirect('crear_posicion')
        elif 'eliminar' in request.POST:
            if posicion:
                posicion.delete()
                messages.warning(request, 'Fue eliminado exitosamente')
                return redirect('crear_posicion')
    return redirect('crear_posicion')

# Crear Posición
def crear_posicion(request):
    if request.method == 'POST':
        form = PosicionForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.nombre = categoria.nombre.capitalize()
            categoria.save()
            messages.success(request, f'{categoria.nombre} Fue guardado exitosamente')
        else:
            messages.error(request, form.errors)

    form = PosicionForm()
    items = Posicion.objects.all()
    context = {
        'form': form,
        'items': items,
        }
    return render(request, 'crear_posicion.html', context)

# Crear Categoría
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fue creado con exito')
        else:
            print(form.errors)
            messages.error(request, f'{form.errors}, Fue creado con exito')

    form = CategoriaForm()
    items = Categoria.objects.all()
    context = {
        'form': form,
        'items': items,
        }
    return render(request, 'crear_categorias.html', context)

# elimina y actualiza categoria
def actualizar_categoria(request, pk):
    if pk:
        categoria = get_object_or_404(Categoria, pk=pk)
    else:
        categoria = None
    if request.method == 'POST':
        if 'editar' in request.POST:
            nuevo = request.POST.get('actualizar')
            nuevo_capitalizado = nuevo.capitalize()  # Capitaliza el número
            
            # Verificar si el nombre ya existe
            if Categoria.objects.filter(nombre=nuevo_capitalizado).exists():
                categoria.save()
                messages.warning(request, f'{categoria.nombre} Esta posición ya existe.')
            else:
                categoria.nombre = nuevo_capitalizado
                categoria.save()  # Guardar el objeto directamente
                messages.info(request, f'{categoria.nombre} Se actualizo exitosamente')
                return redirect('crear_categoria')
        elif 'eliminar' in request.POST:
            if categoria:
                categoria.delete()
                messages.info(request, 'Se elimino exitosamente')
                return redirect('crear_categoria')
    return redirect('crear_categoria')

# Crear
def crear_post(request):
    if request.method == "POST":
        if request.POST.get('posicion') and request.POST.get('categoria'):
            form = PostForm(request.POST)
            categorias_valor = request.POST.get('categoria')
            posicion_valor = request.POST.get('posicion')

            
            if categorias_valor:
                form.fields['categoria'].initial = categorias_valor
            if posicion_valor:
                form.fields['posicion'].initial = posicion_valor

            if form.is_valid():
                form.save()
                return redirect('listar_posts')
            else:
                print(form.errors)  # Esto es útil para depuración
        else:
            if form.is_valid():
                form.save()
            else:
                print(form.errors)

    else:
        form = PostForm()
    context = {
        'form':form
    }
    return render(request, 'crear_post.html', context)

# Leer
def listar_posts(request):
    posts = Post.objects.all()
    return render(request, 'list_post.html', {'posts': posts})

def detalle_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'detalle_post.html', {'post': post})

# Actualizar
def actualizar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('detalle_post', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'actualizar_post.html', {'form': form})

# Eliminar
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect('listar_posts')
    return render(request, 'eliminar_post.html', {'post': post})

