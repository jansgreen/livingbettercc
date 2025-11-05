from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactoForm
from django.core.mail import send_mail, EmailMessage
from dashboard.page.models import Page, PageSection, Footer, carouselPage
from dashboard.contents.models import ContentPost, ContentCategory
from django.conf import settings
from authentication.models.directives import Directives
from django.db.models import Case, When, IntegerField

# Importa el modelo de biografías

#para borrar 
from shop.cart import Cart


# Create your views here.
def home(request):
    # 1. Obtener la página "Home"
    page = get_object_or_404(Page, slug="home")

    # 2. Obtener sus secciones ordenadas (lógica visual)
    sections = page.sections.all().order_by("row", "column")

    # 3. Carrusel (opcional, si sigues usándolo)
    actividades = carouselPage.objects.all()

    context = {
        "page": page,
        "sections": sections,
        "actividades": actividades,
    }
    return render(request, "index.html", context)


def quienes_somos(request):
    # Buscar la categoría con el slug 'quienes_somos'
    user = request.user
    # Filtrar usuarios con el grupo 'manager' y obtener su perfil

    directives_list = Directives.objects.all().order_by('role')
    # Obtener la categoría y los posts relacionados
    category = PageCategory.objects.filter(slug='quienes_somos').first()
    posts = PageContent.objects.filter(category=category)

    # Contexto para el template
    context = {
        'directives': directives_list,
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

def view_bio(request, pk):
    directives_list = Directives.objects.annotate(
    prioridad=Case( 
        When(role__iexact="CEO", then=0),
        default=1,
        output_field=IntegerField()
    )
).order_by('prioridad', 'role')
    articles = Directives.objects.get(pk=pk)
    context = {
        'directives': directives_list,
        'articles': articles,
    }
    return render(request, 'leer_bio.html', context)
