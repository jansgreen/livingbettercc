from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContactoForm
from django.core.mail import EmailMessage
from django.conf import settings
from authentication.models.directives import Directives
from django.db.models import Case, When, IntegerField, Count, F, Sum
from django.db.models.functions import Coalesce
from dashboard.contents.models import ContentPost, ContentCategory
from gallery.models import Image
from classroom.courses.models import Course
from classroom.courses.models import CourseYearStat
from classroom.certifications.models import Certificate
from classroom.certifications.utils import get_report_activity_grouped_for_tabs
from django.db.models.functions import ExtractYear
from collections import OrderedDict
from shop.cart import Cart
from collections import defaultdict
from .models import ReportActivity

def home(request):
    category = ContentCategory.objects.filter(slug="home").first()
    gallery = Image.objects.filter(forcarousel=True)

    # PRESENCIAL (reportes)
    tabs, issues_by_cat = get_report_activity_grouped_for_tabs()

    # DIGITAL (certificados reales)
    online_total = Certificate.objects.count()
    online_by_year = (
        Certificate.objects
        .values("issued_date__year")
        .annotate(total=Count("id"))
        .order_by("-issued_date__year")
    )

    posts = category.posts.filter(status="published").order_by("-created_at") if category else None

    context = {
        "gallery": gallery,
        "posts": posts,

        # Para estadistica_proyecto.html
        "tabs": tabs,
        "issues_by_cat": issues_by_cat,

        # Impacto digital (si lo quieres mostrar)
        "online_total": online_total,
        "online_by_year": online_by_year,
    }
    return render(request, "index.html", context)


def quienes_somos(request):
    category = ContentCategory.objects.filter(slug="quienes_somos").first()
    directives = Directives.objects.all()

    tabs, issues_by_cat = get_report_activity_grouped_for_tabs()

    posts = category.posts.filter(status="published").order_by("-created_at")[:5] if category else None

    context = {
        "posts": posts,
        "directives": directives,

        # Para estadistica_proyecto.html
        "tabs": tabs,
        "issues_by_cat": issues_by_cat,
    }
    return render(request, "quienes_somos.html", context)

def contactanos(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email_usuario = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']

            # Destino principal
            to_emails = [getattr(settings, "EMAIL_HOST_DEST", settings.EMAIL_HOST_USER)]

            # CC opcional (admins)
            cc_emails = []
            raw_cc = getattr(settings, "EMAIL_HOST_CC", "")
            if isinstance(raw_cc, str):
                cc_emails = [e.strip() for e in raw_cc.split(",") if e.strip()]
            elif isinstance(raw_cc, (list, tuple)):
                cc_emails = list(raw_cc)

            body = (
                f"Nuevo mensaje desde el formulario de contacto\n\n"
                f"Nombre: {nombre}\n"
                f"Email: {email_usuario}\n\n"
                f"Mensaje:\n{mensaje}\n"
            )

            email_message = EmailMessage(
                subject=f"[CONTACTO] {nombre}",
                body=body,
                from_email=settings.EMAIL_HOST_USER,     # emisor autorizado
                to=[settings.EMAIL_HOST_USER],           # TU MISMO BUZÓN (no el usuario)
                reply_to=[email_usuario],                # aquí sí va el usuario
                cc=settings.EMAIL_HOST_CC,
            )
            email_message.send(fail_silently=False)

            # En producción mejor ver errores: fail_silently=False
            email_message.send(fail_silently=False)

            messages.success(request, 'Mensaje enviado exitosamente.')
            return redirect('contactanos')
        else:
            messages.error(request, f'{form.errors}, Por favor corrige los errores a continuación.')
    else:
        form = ContactoForm()

    return render(request, 'contact_us.html', {'form': form})

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

# Reportes de certificaciones presencialess
# certifications/utils.py (o donde tengas helpers)
