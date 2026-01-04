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
from classroom.certifications.models import Certificate, InPersonCategory, InPersonCertificateIssue
from classroom.courses.models import CourseYearStat
from classroom.courses.services.taod_stats import get_taod_stats
from classroom.certifications.views import get_inperson_stats_by_course
from classroom.certifications.services.taod_from_inperson import get_taod_stats_from_inperson_issues
from django.db.models.functions import ExtractYear
from collections import OrderedDict
from shop.cart import Cart
from collections import defaultdict


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

def _get_inperson_issues_grouped_for_tabs():
    # 1) Traer issues con relaciones
    issues = list(
        InPersonCertificateIssue.objects
        .select_related("course", "category")
        .order_by("-issued_date", "-updated_at")
    )

    # 2) Totales por AÑO y por CATEGORÍA (para TAOD "desde")
    year_rows = (
        InPersonCertificateIssue.objects
        .annotate(year=ExtractYear("issued_date"))
        .values("category_id", "year")
        .annotate(
            sum_presencial=Sum("quantity"),
            sum_online=Sum("impact"),
        )
    )

    # year_totals[(cat_id_or_0, year)] -> {"pres": X, "onl": Y}
    year_totals = {}
    for r in year_rows:
        cat_id = r["category_id"] or 0
        year_totals[(cat_id, r["year"])] = {
            "pres": r["sum_presencial"] or 0,
            "onl": r["sum_online"] or 0,
        }

    # 3) Primero: calcular "desde" por issue (crea desde_presencial_total / desde_online_total)
    for issue in issues:
        cat_id = issue.category_id or 0

        if not issue.issued_date:
            issue.prev_year = None
            issue.desde_presencial_total = 0
            issue.desde_online_total = 0
            continue

        current_year = issue.issued_date.year
        prev_year = current_year - 1
        issue.prev_year = prev_year

        prev_vals = year_totals.get((cat_id, prev_year), {"pres": 0, "onl": 0})
        curr_vals = year_totals.get((cat_id, current_year), {"pres": 0, "onl": 0})

        issue.desde_presencial_total = prev_vals["pres"] + curr_vals["pres"]
        issue.desde_online_total = prev_vals["onl"] + curr_vals["onl"]

    # 4) Ahora: progreso basado en TAOD presencial (por categoría)
    cat_totals = defaultdict(list)
    for i in issues:
        cat_id = i.category_id or 0
        cat_totals[cat_id].append(i.desde_presencial_total or 0)

    cat_max = {cat_id: (max(vals) if vals else 0) for cat_id, vals in cat_totals.items()}

    for issue in issues:
        cat_id = issue.category_id or 0
        max_val = cat_max.get(cat_id, 0)
        val = issue.desde_presencial_total or 0

        if max_val > 0:
            pct = int(round((val / max_val) * 100))
            pct = max(1 if val > 0 else 0, min(100, pct))
        else:
            pct = 0

        issue.pct_total = pct
        issue.total_impact = int((issue.quantity or 0) + (issue.impact or 0))  # por si lo sigues usando

    # 5) Tabs dinámicos (solo categorías con contenido + "Sin categoría" si aplica)
    categories = list(InPersonCategory.objects.order_by("name"))
    tabs = OrderedDict()

    for c in categories:
        tabs[c.id] = c.name

    has_uncat = any(i.category_id is None for i in issues)
    if has_uncat:
        tabs[0] = "Otros"

    # 6) Agrupar issues por categoría
    issues_by_cat = {}
    for issue in issues:
        cat_id = issue.category_id or 0
        issues_by_cat.setdefault(cat_id, []).append(issue)

    tabs_with_content = [(cat_id, name) for cat_id, name in tabs.items() if issues_by_cat.get(cat_id)]

    return tabs_with_content, issues_by_cat

def home(request):
    # 1. Obtener la página "Home"
    category = ContentCategory.objects.filter(slug="home").first()
    # Solo imágenes marcadas para el carrusel
    gallery = Image.objects.filter(forcarousel=True)

    online = Certificate.objects.all()
    tabs, issues_by_cat = _get_inperson_issues_grouped_for_tabs()
    categories = InPersonCategory.objects.order_by("name")


    if category:
        posts = category.posts.filter(status="published").order_by("-created_at")
    else:
        posts = None

    context = {
        'gallery': gallery,
        'posts': posts,
        'tabs': tabs,
        'issues_by_cat': issues_by_cat,
        'online_impact': online,
        'categories': categories,

    }

    return render(request, "index.html", context)

def quienes_somos(request):
    category = ContentCategory.objects.filter(slug='quienes_somos').first()
    directives = Directives.objects.all()
    tabs, issues_by_cat = _get_inperson_issues_grouped_for_tabs()
    categories = InPersonCategory.objects.order_by("name")
    if category:
        posts = category.posts.filter(
            status="published"
        ).order_by("-created_at")[:5]
    else:
        posts = None

    context = {
        "posts": posts,
        "directives": directives,
        'tabs': tabs,
        'issues_by_cat': issues_by_cat,
        'categories': categories,
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

def estadistica_proyectos(request):
    issues = InPersonCertificateIssue.objects.all()
    issues = issues.annotate(
        year=ExtractYear('issued_date'),
    )
    year_totals = (
        issues.values('year')
        .annotate(
            presencial_total=Sum('quantity'),
            online_total=Sum('impact')
        )
    )

    # Convertimos a diccionario para acceso rápido
    year_totals_map = {
        y['year']: y for y in year_totals
    }

    # Pegamos los totales a cada objeto
    for i in issues:
        totals = year_totals_map.get(i.year, {})
        i.year_presencial_total = totals.get('presencial_total', 0)
        i.year_online_total = totals.get('online_total', 0)

    context = {
        'inperson_issues': issues
    }
