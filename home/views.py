from blog.models import Post, Categoria
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactoForm
from django.core.mail import send_mail, EmailMessage
from page.models import Footer, Column, ImagenPage, PageContent
from authentication.models import Biography
from django.conf import settings



# Create your views here.
def home(request):
    habilidades = ImagenPage.objects.filter(category__nombre__in=["Ministerio de Educacion", "Ministerio de Salud"])
    actividades = ImagenPage.objects.filter(category__nombre__in=["Actividades",])
    columns = Column.objects.prefetch_related('contents').all()  # Utiliza prefetch_related para optimizar las consultas
    context = {
        'actividades': actividades,
        'habilidades':habilidades,
        'columns': columns,
    }
    return render(request, 'index.html', context)

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

def aboutUs(request):
    biography = Biography.objects.all()
    categoria_biografia = Categoria.objects.get(nombre="Biografia")
    columns = Column.objects.prefetch_related('contents').all()  # Utiliza prefetch_related para optimizar las consultas
    directivas = Post.objects.filter(categoria=categoria_biografia) 
    is_directivas_member = request.user.groups.filter(name="directivas").exists()
    context={
        'biography':biography,
        'columns':columns,
        'is_directivas_member':is_directivas_member,
        'directivas': directivas,
    }
    return render(request, 'quienes_somos.html', context)

def leerBio(request, pk):
    biography = Biography.objects.filter(user=pk) 
    is_directivas_member = request.user.groups.filter(name="directivas").exists()
    context={
        'singlePage': True,
        'biography':biography,
        'is_directivas_member':is_directivas_member,
    }
    return render(request, 'leer_bio.html', context)

def contactanos(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Obtén los datos del formulario
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']

            # Crea el contenido del correo
            email_message = EmailMessage(
                subject=f'Mensaje de contacto de {nombre}',
                body=f'Mensaje: {mensaje}\n\nDe: {nombre} <{email}>',
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_DEST,],  # Cambia esto al correo de destino
            )
            email_message.cc = [email]
            cc_emails = settings.EMAIL_HOST_CC  # Suponiendo que estos son los correos para CC
            for cc_email in cc_emails:
                email_message.cc.append(cc_email)
    
    # Enviar el correo
            email_message.send(fail_silently=False)
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

def single_page(request, pk):
    post = [getPost for getPost in PageContent.objects.filter(pk=pk)]
    context = {
        'post':post,
    }
    return render(request, 'home_single_page.html', context)