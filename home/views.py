from blog.models import Post
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactoForm
from django.core.mail import send_mail
from page.models import Footer


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
    es_directiva = request.user.groups.filter(name='directivas').exists() if request.user.is_authenticated else False
    post = Post.objects.filter(posicion__nombre__startswith='biografia-')
    context = {
        'es_directiva': es_directiva,
        'Qpages': True,
        'posts': post,
    }
    return render(request, 'quienes_somos.html', context)

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

