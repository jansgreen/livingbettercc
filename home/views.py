from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactoForm
from django.core.mail import send_mail, EmailMessage
from dashboard.page.models import Footer, PagePosition, PageContent, PageCategory, carouselPage

from django.conf import settings
from django.contrib.auth.models import User

#para borrar 
from shop.cart import Cart




# Create your views here.
def home(request):
    posts = PageContent.objects.all()
    actividades = carouselPage.objects.all()
    # Contexto para el template
    context = {
        'posts': posts,
        'actividades': actividades,
    }
    return render(request, 'index.html', context)

def quienes_somos(request):
    # Buscar la categoría con el slug 'quienes_somos'
    user = request.user
    # Filtrar usuarios con el grupo 'manager' y obtener su perfil
    managers = User.objects.filter(groups__name='manager').select_related('profile')

    # Ordenar los managers colocando a los que tienen el roll 'CEO' primero
    managers = sorted(managers, key=lambda x: x.profile.roll != 'CEO')

    # Obtener la categoría y los posts relacionados
    category = PageCategory.objects.filter(slug='quienes_somos').first()
    posts = PageContent.objects.filter(category=category)

    # Contexto para el template
    context = {
        'managers': managers,
        'posts': posts,
        'user': user,
    }

    return render(request, 'quienes_somos.html', context)


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
            email_message.send(fail_silently=True)
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
    article = get_object_or_404(PageContent, pk=pk)
    related_articles = PageContent.objects.filter(category=article.category).exclude(pk=article.pk)[:3]
    
    # Renderizar el template con el contexto
    return render(request, 'leerpageweb.html', {
        'article': article,
        'related_articles': related_articles,
    })
