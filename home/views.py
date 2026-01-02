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
from classroom.certifications.models import Certificate, InPersonCertificateIssue
from classroom.courses.models import CourseYearStat
from classroom.courses.services.taod_stats import get_taod_stats
from classroom.certifications.views import get_inperson_stats_by_course
from classroom.certifications.services.taod_from_inperson import get_taod_stats_from_inperson_issues


def _attach_course_year_breakdown(courses_queryset):
    courses = list(courses_queryset)
    if not courses:
        return courses

    course_ids = [c.id for c in courses]

    auto_rows = (
        Certificate.objects.filter(course_id__in=course_ids)
        .values('course_id', 'issued_date__year')
        .annotate(auto_count=Count('id'))
    )
    auto_map = {}
    for row in auto_rows:
        cid = row['course_id']
        year = row['issued_date__year']
        if year is None:
            continue
        auto_map.setdefault(cid, {})[int(year)] = int(row['auto_count'])

    manual_rows = CourseYearStat.objects.filter(course_id__in=course_ids)
    manual_map = {}
    for stat in manual_rows:
        manual_map.setdefault(stat.course_id, {})[int(stat.year)] = {
            'manual_add': int(stat.manual_certified_add),
            'note': stat.note,
        }

    for course in courses:
        years = set(auto_map.get(course.id, {}).keys()) | set(manual_map.get(course.id, {}).keys())
        if not years:
            course.year_breakdown = []
            continue

        stats = []
        for year in sorted(years):
            auto_count = int(auto_map.get(course.id, {}).get(year, 0))
            manual_info = manual_map.get(course.id, {}).get(year, {})
            manual_add = int(manual_info.get('manual_add', 0))
            total = auto_count + manual_add
            stats.append({
                'year': year,
                'auto': auto_count,
                'manual': manual_add,
                'total': total,
                'note': manual_info.get('note', ''),
            })

        max_total = max(s['total'] for s in stats) if stats else 0
        for s in stats:
            s['pct'] = int(round((s['total'] / max_total) * 100)) if max_total else 0
        course.year_breakdown = stats

    return courses

# Importa el modelo de biografías

#para borrar 
from shop.cart import Cart


def _get_inperson_issues_for_cards():
    issues = list(
        InPersonCertificateIssue.objects
        .select_related('course')
        .order_by('-issued_date', '-updated_at')
    )

    totals = [int((i.quantity or 0) + (i.impact or 0)) for i in issues]
    max_total = max(totals) if totals else 0

    for issue, total in zip(issues, totals):
        issue.total_impact = total
        if max_total > 0:
            pct = int(round((total / max_total) * 100))
            pct = max(0, min(100, pct))
            if total > 0 and pct == 0:
                pct = 1
        else:
            pct = 0
        issue.pct_total = pct

    return issues


# Create your views here.
def home(request):
    # 1. Obtener la página "Home"
    category = ContentCategory.objects.filter(slug="home").first()
    # Solo imágenes marcadas para el carrusel
    gallery = Image.objects.filter(forcarousel=True)

    online = Certificate.objects.all()
    inperson_issues = _get_inperson_issues_for_cards()


    if category:
        posts = category.posts.filter(status="published").order_by("-created_at")
    else:
        posts = None

    context = {
        'gallery': gallery,
        'posts': posts,
        'inperson_issues': inperson_issues,
        'online_impact': online,

    }

    return render(request, "index.html", context)

def quienes_somos(request):
    category = ContentCategory.objects.filter(slug='quienes_somos').first()
    directives = Directives.objects.all()
    inperson_issues = _get_inperson_issues_for_cards()
    if category:
        posts = category.posts.filter(
            status="published"
        ).order_by("-created_at")[:5]
    else:
        posts = None

    context = {
        "posts": posts,
        "directives": directives,
        'inperson_issues': inperson_issues,
    }


    return render(request, 'quienes_somos.html', context)

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
                subject=f"[CONTACTO] Mensaje de {nombre}",
                body=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
                to=to_emails,
                cc=cc_emails,
                reply_to=[email_usuario],  # CLAVE: responder al usuario sin “suplantar”
            )

            # En producción mejor ver errores: fail_silently=False
            email_message.send(fail_silently=False)

            messages.success(request, 'Mensaje enviado exitosamente.')
            return redirect('contactanos')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
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
