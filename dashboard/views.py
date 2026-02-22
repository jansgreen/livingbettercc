from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.forms import inlineformset_factory
from django.forms import NumberInput, TextInput

from django.db.models import Count, Sum, Value, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone

# Import app models used for dashboard counts
from authentication.models.students import Students
from authentication.models.customers import Customers
from formbuilder.models import FormDefinition

from classroom.courses.models import Course, Program
from classroom.courses.services.taod_stats import get_taod_stats  # <- usa el actualizado (o el path que tengas)

from classroom.certifications.models import Certificate
from classroom.enrollments.models import BecaApplication

# 🔁 AJUSTA ESTE IMPORT a tu ubicación real
from home.models import ReportActivity
# o: from classroom.reports.models import ReportActivity


# -----------------------------
# Helpers
# -----------------------------
def get_report_activity_stats():
    """
    Stats presenciales (ReportActivity) para el dashboard.
    - total_quantity: suma global
    - by_course: suma por curso
    - by_year: suma por año
    """
    total_quantity = (
        ReportActivity.objects.aggregate(total=Coalesce(Sum("quantity"), 0))["total"] or 0
    )

    by_course = list(
        ReportActivity.objects.values("course__id", "course__title")
        .annotate(total=Coalesce(Sum("quantity"), 0))
        .order_by("-total", "course__title")
    )

    by_year = list(
        ReportActivity.objects.values("issued_year")
        .annotate(total=Coalesce(Sum("quantity"), 0))
        .order_by("-issued_year")
    )

    return {
        "total_quantity": int(total_quantity),
        "by_course": by_course,
        "by_year": by_year,
    }


# -----------------------------
# Becas
# -----------------------------
@csrf_exempt
def beca_application_action(request, app_id):
    if not request.user.is_staff or request.method != "POST":
        return redirect("beca_applications_list")

    app = get_object_or_404(BecaApplication, id=app_id)
    action = request.POST.get("action")

    if action == "aprobar":
        app.status = "approved"
        app.save()
    elif action == "rechazar":
        app.status = "rejected"
        app.save()

    return redirect("beca_applications_list")


def beca_applications_list(request):
    if not request.user.is_staff:
        return render(request, "dashboard/dashboard_base.html", {"error": "No autorizado"})

    estado = request.GET.get("estado", "todos")
    qs = (
        BecaApplication.objects.select_related("user", "course", "address")
        .order_by("-fecha_aplicacion")
    )

    if estado != "todos":
        estado_map = {
            "aprobada": "approved",
            "rechazada": "rejected",
            "pendiente": "submitted",
        }
        qs = qs.filter(status=estado_map.get(estado, estado))

    return render(
        request,
        "dashboard/beca_applications_list.html",
        {"beca_applications": qs, "estado": estado},
    )

# -----------------------------
# Dashboard principal
# -----------------------------
@login_required
def dashboards(request):
    """
    Dashboard overview con:
    - contadores generales
    - stats por curso (online + presencial)
    - stats TAOD (KPIs, por año, top cursos) usando tu nueva lógica
    """
    students_count = Students.objects.count()
    users_count = User.objects.count()
    forms_count = FormDefinition.objects.count()
    courses_count = Course.objects.count()
    customers_count = Customers.objects.count()

    beca_applications_count = BecaApplication.objects.count()
    becados_count = BecaApplication.objects.filter(status="approved").count()

    user_groups = (
        set(request.user.groups.values_list("name", flat=True))
        if request.user.is_authenticated
        else set()
    )

    # -----------------------------
    # Stats por curso (nuevo sistema)
    #   - online_certified_count: Certificate
    #   - in_person_total: ReportActivity.quantity (suma)
    #   - total_certified_count: online + presencial
    # -----------------------------
    # Subquery libre: hacemos dos queries y merge en python (más simple + cero Subquery bugs)
    online_by_course = {
        row["course_id"]: int(row["total"] or 0)
        for row in (
            Certificate.objects.values("course_id")
            .annotate(total=Count("id"))
        )
    }

    inperson_by_course = {
        row["course_id"]: int(row["total"] or 0)
        for row in (
            ReportActivity.objects.values("course_id")
            .annotate(total=Coalesce(Sum("quantity"), 0))
        )
    }

    courses_stats = []
    for c in Course.objects.all().order_by("-published", "title"):
        online = int(online_by_course.get(c.id, 0))
        in_person = int(inperson_by_course.get(c.id, 0))
        courses_stats.append(
            {
                "pk": c.pk,
                "title": c.title,
                "published": getattr(c, "published", False),
                "auto_certified_count": online,
                "in_person_total": in_person,
                "total_certified_count": online + in_person,
                "description": getattr(c, "description", ""),
            }
        )

    # Ordena por total desc
    courses_stats.sort(key=lambda x: (x["total_certified_count"], x["title"]), reverse=True)

    # -----------------------------
    # TAOD (nuevo get_taod_stats)
    # -----------------------------
    taod = get_taod_stats(top_n=10)

    # Stats presenciales globales (para widgets del dashboard)
    inperson_stats = get_report_activity_stats()

    context = {
        "students_count": students_count,
        "users_count": users_count,
        "forms_count": forms_count,
        "courses_count": courses_count,
        "customers_count": customers_count,

        "beca_applications_count": beca_applications_count,
        "becados_count": becados_count,

        "is_student": "estudiantes" in user_groups,
        "is_tecnico": "tecnicos" in user_groups,
        "is_facilitador": "facilitadores" in user_groups,

        "courses_stats": courses_stats,
        "inperson_stats": inperson_stats,

        "taod_kpis": taod.taod_kpis,
        "taod_years": taod.taod_years,
        "top_courses": taod.top_courses,
    }

    # Si tu template usaba taod_courses, lo dejamos, pero ahora coherente:
    taod_program = Program.objects.filter(name="TAOD").first()
    if taod_program:
        taod_course_ids = list(Course.objects.filter(program=taod_program).values_list("id", flat=True))

        # armar cursos TAOD con totals (online + presencial)
        taod_online = {
            row["course_id"]: int(row["total"] or 0)
            for row in (
                Certificate.objects.filter(course_id__in=taod_course_ids)
                .values("course_id")
                .annotate(total=Count("id"))
            )
        }
        taod_inperson = {
            row["course_id"]: int(row["total"] or 0)
            for row in (
                ReportActivity.objects.filter(course_id__in=taod_course_ids)
                .values("course_id")
                .annotate(total=Coalesce(Sum("quantity"), 0))
            )
        }

        taod_courses = []
        for c in Course.objects.filter(id__in=taod_course_ids).order_by("title"):
            online = int(taod_online.get(c.id, 0))
            in_person = int(taod_inperson.get(c.id, 0))
            taod_courses.append(
                {
                    "pk": c.pk,
                    "title": c.title,
                    "auto_certified_count": online,
                    "in_person_total": in_person,
                    "total_certified_count": online + in_person,
                    "blurb": getattr(c, "description", ""),
                }
            )
        taod_courses.sort(key=lambda x: (x["total_certified_count"], x["title"]), reverse=True)
    else:
        taod_courses = []

    context["taod_courses"] = taod_courses

    return render(request, "dashboard.html", context)


# -----------------------------
# ⚠️ CourseYearStat editor
# -----------------------------
# Si YA NO usarás CourseYearStat, lo mejor es eliminar esta vista y su URL.
# Te la dejo “apagada” con un mensaje claro.
def course_year_stats_edit(request, pk):
    if not request.user.is_staff:
        return render(request, "dashboard/dashboard_base.html", {"error": "No autorizado"})

    messages.warning(
        request,
        "Esta sección (CourseYearStat) pertenece al sistema anterior. "
        "Ahora usamos ReportActivity para reportes presenciales."
    )
    return redirect("dashboard")
