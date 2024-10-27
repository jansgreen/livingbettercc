from blog.models import Post, Categoria
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactoForm
from django.core.mail import send_mail
from page.models import Footer
from authentication.models import Biography


# Create your views here.


def BioUser(request, pk):
    es_directiva = request.user.groups.filter(name='directivas').exists() if request.user.is_authenticated else False
    posts = Post.objects.filter(posicion__nombre__startswith='biografia-')
    biografia = Post.objects.filter(pk=pk)
    context = {
        'es_directiva':es_directiva,
        'biografia': biografia,
        'posts': posts,

    }
    return render(request, 'quienes_somos.html', context)

def home(request):
    post_1 = Post.objects.filter(posicion__nombre='Column-1')
    posts_2 = Post.objects.filter(posicion__nombre='Column-2')
    posts_3 = Post.objects.filter(posicion__nombre='Column-3')

    context = {
        'posts_1': post_1,
        'posts_2': posts_2,
        'posts_3': posts_3,
    }
    return render(request, 'index.html', context)

def aboutUs(request):
    biography = Biography.objects.all()
    categoria_biografia = Categoria.objects.get(nombre="Biografia")
    categoria_quienes_somos = Categoria.objects.get(nombre="About")
    posts = Post.objects.filter(categoria=categoria_quienes_somos)
    directivas = Post.objects.filter(categoria=categoria_biografia) 
    is_directivas_member = request.user.groups.filter(name="directivas").exists()
    context={
        'biography':biography,
        'posts':posts,
        'is_directivas_member':is_directivas_member,
        'directivas': directivas,
    }
    return render(request, 'quienes_somos.html', context)

def leerBio(request, pk):
    biography = Biography.objects.filter(user=pk) 
    is_directivas_member = request.user.groups.filter(name="directivas").exists()
    context={
        'biography':biography,
        'is_directivas_member':is_directivas_member,
    }
    return render(request, 'leer_bio.html', context)

def contactanos(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Enviar correo electrónico
            subject = 'Nuevo mensaje de contacto'
            message = f'Nombre: {form.cleaned_data["nombre"]}\nEmail: {form.cleaned_data["email"]}\nMensaje: {form.cleaned_data["mensaje"]}'
            from_email = form.cleaned_data['email']
            send_mail(subject, message, from_email, ['jansgreen@gmail.com'])
            
            # Guardar en la base de datos
            form.save()
            messages.success(request, 'Mensaje enviado exitosamente.')
            return redirect('contactanos')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = ContactoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'contact_us.html', context)

