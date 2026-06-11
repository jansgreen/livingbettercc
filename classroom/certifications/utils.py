# classroom/certifications/utils.py
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Tuple

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.db.models import IntegerField
from django.db.models.functions import ExtractYear
from django.utils import timezone

from classroom.certifications.models import Certificate
from home.models import ReportActivity, ReportCategories
from decimal import Decimal


def _clamp_pct(v: int) -> int:
    return max(0, min(100, int(v)))

def get_report_activity_grouped_for_tabs(*, limit_years: int = 6) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]]]:
    """
    Tabs por categoría.
    Cada tab muestra impactos por año/distrito, combinando:
      - Presencial (ReportActivity.quantity)
      - Digital/Online (count de Certificate por curso y año)

    Retorna:
      tabs: [(tab_id, tab_name)]
      issues_by_cat: {tab_id: [dict impacto, ...]}
    """

    current_year = timezone.now().year
    min_year = current_year - max(0, limit_years - 1)

    # Presencial
    ra_qs = (
        ReportActivity.objects
        .select_related("course", "categories")
        .filter(issued_year__gte=min_year)
        .order_by("-issued_year", "district")
    )

    # Digital: contar certificados emitidos por curso/año
    cert_counts_qs = (
        Certificate.objects
        .filter(issued_date__year__gte=min_year)
        .annotate(y=ExtractYear("issued_date"))
        .values("course_id", "y")
        .annotate(total=Count("id"))
    )

    digital_by_course_year = {
        (int(r["course_id"]), int(r["y"])): int(r["total"] or 0)
        for r in cert_counts_qs
        if r.get("course_id") is not None and r.get("y") is not None
    }

    # Tabs: categorías que tengan presencial o digital
    category_map: Dict[int, Any] = {}
    for ra in ra_qs:
        if ra.categories_id:
            category_map[ra.categories_id] = ra.categories

    categories = sorted(category_map.values(), key=lambda x: (x.name or "").lower())
    tabs: List[Tuple[str, str]] = [(str(cat.id), cat.name) for cat in categories]
    issues_by_cat: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    # Precálculo: totales acumulados por curso/año
    presencial_qty_by_course_year = defaultdict(int)
    years_by_course = defaultdict(set)
    for ra in ra_qs:
        presencial_qty_by_course_year[(ra.course_id, ra.issued_year)] += int(ra.quantity or 0)
        years_by_course[ra.course_id].add(ra.issued_year)

    presencial_sum_by_course_year = defaultdict(int)  # acumulado hasta ese año (ascendente)
    for course_id, years in years_by_course.items():
        running = 0
        for y in sorted(years):  # ascendente para acumular
            running += presencial_qty_by_course_year[(course_id, y)]
            presencial_sum_by_course_year[(course_id, y)] = running

    # ✅ FIX: "Total Presencial desde {año}" en tu UX realmente es acumulado HASTA ese año:
    # 2021 -> 29
    # 2022 -> 29+88
    # 2023 -> 29+88+1325 ...
    def sum_presencial_hasta(course_id: int, year: int) -> int:
        return sum(
            v for (cid, y), v in presencial_qty_by_course_year.items()
            if cid == course_id and y <= year
        )

    def sum_digital_hasta(course_id: int, year: int) -> int:
        return sum(
            v for (cid, y), v in digital_by_course_year.items()
            if cid == course_id and y <= year
        )

    # Para cada categoría/tab, creamos items por ReportActivity
    # Y añadimos digital en el mismo “impact row”
    for cat in categories:
        tab_id = str(cat.id)

        # Filtrar reportes de esta categoría
        pres_rows = [ra for ra in ra_qs if ra.categories_id == cat.id]
        course_ids = {ra.course_id for ra in pres_rows if ra.course_id}

        # Agrupar por curso dentro de la categoría
        for course_id in course_ids:
            course = None
            for ra in pres_rows:
                if ra.course_id == course_id:
                    course = ra.course
                    break

            years_present = sorted({ra.issued_year for ra in pres_rows if ra.course_id == course_id}, reverse=True)
            digital_years = sorted({y for (cid, y), v in digital_by_course_year.items() if cid == course_id and v > 0}, reverse=True)
            all_years = sorted(set(years_present) | set(digital_years), reverse=True)[:max(1, limit_years)]

            max_total_for_course = 0
            totals_for_course_year = {}

            for y in all_years:
                pres_total = int(presencial_sum_by_course_year.get((course_id, y), 0))
                dig_total = int(digital_by_course_year.get((course_id, y), 0))
                tot = pres_total + dig_total
                totals_for_course_year[y] = tot
                max_total_for_course = max(max_total_for_course, tot)

            for y in all_years:
                rows_this_year = [ra for ra in pres_rows if ra.course_id == course_id and ra.issued_year == y]
                if not rows_this_year:
                    rows_this_year = [None]

                for ra in rows_this_year:
                    presencial_qty = int(getattr(ra, "quantity", 0) or 0)
                    digital_qty = int(digital_by_course_year.get((course_id, y), 0))

                    total_year = int(totals_for_course_year.get(y, presencial_qty + digital_qty))
                    pct_total = 0
                    if max_total_for_course > 0:
                        pct_total = int(round((total_year / max_total_for_course) * 100))
                        pct_total = _clamp_pct(pct_total)
                        if total_year > 0 and pct_total == 0:
                            pct_total = 1

                    prev_year = y
                    # ✅ FIX AQUI: usar acumulado hasta el año (<= y), no desde el año (>= y)
                    desde_pres = sum_presencial_hasta(course_id, prev_year)
                    desde_dig = sum_digital_hasta(course_id, prev_year)

                    issues_by_cat[tab_id].append(
                        {
                            "course": course,
                            "issued_date": date(y, 1, 1),
                            "district": getattr(ra, "district", "—") if ra else "—",
                            "quantity": presencial_qty,
                            "impact": digital_qty,
                            "pct_total": pct_total,
                            "prev_year": prev_year,
                            "desde_presencial_total": desde_pres,
                            "desde_online_total": desde_dig,
                            "image": getattr(ra, "image", None) if ra else None,
                            "note": getattr(ra, "description", "") if ra else "",
                            "updated_at": getattr(ra, "created_at", None) if ra else None,
                        }
                    )

    return tabs, dict(issues_by_cat)


def get_online_certificates_by_course_year(*, limit_years: int = 6) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]]]:
    """
    Genera reportes de certificaciones online agrupadas por course + year.

    Obtiene automáticamente datos de Certificate y los agrupa por:
    - course_id + year
    - Cuenta cantidad de certificados
    - Extrae distritos de ScholarshipStudentInfo de usuarios

    Combina con datos de OnlineCertificateReport para imagen/descripción.

    Retorna formato similar a get_report_activity_grouped_for_tabs():
      tabs: [(tab_id, tab_name)] - categoría única "ONLINE"
      issues_by_cat: {tab_id: [dict reporte, ...]}
    """
    from classroom.certifications.models import OnlineCertificateReport
    from django.db.models import Q, F, CharField
    from django.db.models.functions import Coalesce

    current_year = timezone.now().year
    min_year = current_year - max(0, limit_years - 1)
    return _get_online_certificates_by_course_year_v2(min_year=min_year)

    # Obtener certificados con info de distrito del usuario
    # Solo incluir certificados donde el usuario tiene scholarship_info con district válido
    cert_data = (
        Certificate.objects
        .filter(
            pending=False,
            issued_date__year__gte=min_year,
            user__scholarship_info__isnull=False,
            user__scholarship_info__district__isnull=False
        )
        .select_related("course", "user__scholarship_info")
        .annotate(
            y=ExtractYear("issued_date"),
            district=F("user__scholarship_info__district")
        )
        .values("course_id", "y", "district")
        .annotate(count=Count("id"))
        .order_by("course_id", "-y", "district")
    )

    # Agrupar por course_id + year para obtener lista de distritos y total
    certs_by_course_year = defaultdict(lambda: {"districts": set(), "count": 0})

    for row in cert_data:
        key = (row["course_id"], row["y"])
        # Formatear distrito como string con leading zero si es necesario
        district_str = f"{int(row['district']):02d}" if row["district"] else None
        if district_str:
            certs_by_course_year[key]["districts"].add(district_str)
        certs_by_course_year[key]["count"] += row["count"]

    # Auto-crear registros OnlineCertificateReport si no existen
    for (course_id, year), cert_info in certs_by_course_year.items():
        districts_str = ", ".join(sorted(cert_info["districts"]))
        total_qty = cert_info["count"]

        # Crear o actualizar OnlineCertificateReport
        report, created = OnlineCertificateReport.objects.update_or_create(
            course_id=course_id,
            issued_year=year,
            defaults={
                "total_quantity": total_qty,
                "districts_list": districts_str,
            }
        )

    # Obtener cursos para acceso a títulos
    from classroom.courses.models import Course
    courses = {c.id: c for c in Course.objects.filter(id__in=set(k[0] for k in certs_by_course_year.keys()))}

    # Obtener datos de OnlineCertificateReport para imagen/descripción
    online_reports = {
        (r.course_id, r.issued_year): r
        for r in OnlineCertificateReport.objects.filter(issued_year__gte=min_year)
    }

    # Construir estructura de tabs (categoría única: ONLINE)
    tabs = [("online", "ONLINE")]
    issues_by_cat = {"online": []}

    # Construir items de reporte
    for (course_id, year), cert_info in sorted(certs_by_course_year.items(), key=lambda x: (-x[0][1], x[0][0])):
        course = courses.get(course_id)
        if not course:
            continue

        districts_str = ", ".join(sorted(cert_info["districts"]))
        total_qty = cert_info["count"]

        # Obtener datos editables de OnlineCertificateReport si existe
        report = online_reports.get((course_id, year))
        image = getattr(report, "image", None) if report else None
        description = getattr(report, "description", "") if report else ""
        updated_at = getattr(report, "updated_at", timezone.now()) if report else timezone.now()

        issues_by_cat["online"].append({
            "course": course,
            "issued_date": date(year, 1, 1),
            "district": districts_str,
            "quantity": 0,  # Para presencial (no aplica para online)
            "impact": total_qty,  # Cantidad online
            "pct_total": None,  # No calcular porcentaje para online
            "prev_year": year - 1 if year > min_year else min_year,
            "desde_presencial_total": None,
            "desde_online_total": None,
            "image": image,
            "note": description,
            "updated_at": updated_at,
            "report_id": report.id if report else None,  # ID para editar
            "is_online": True,  # Indicador de que es online
        })

    return tabs, dict(issues_by_cat)


def _get_online_certificates_by_course_year_v2(*, min_year: int) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]]]:
    from authentication.models.profiles import ScholarshipStudentInfo
    from classroom.certifications.models import OnlineCertificateReport
    from django.db.models import F

    country_labels = dict(ScholarshipStudentInfo.COUNTRY_CHOICES)
    cert_data = (
        Certificate.objects
        .filter(pending=False, issued_date__year__gte=min_year)
        .select_related("course", "user__scholarship_info")
        .annotate(
            y=ExtractYear("issued_date"),
            district=F("user__scholarship_info__district"),
            regional=F("user__scholarship_info__regional"),
            province=F("user__scholarship_info__province"),
            country=F("user__scholarship_info__country"),
        )
        .values("course_id", "y", "district", "regional", "province", "country")
        .annotate(count=Count("id"))
        .order_by("course_id", "-y", "district", "regional")
    )

    certs_by_course_year = defaultdict(
        lambda: {
            "districts": set(),
            "regionals": set(),
            "provinces": set(),
            "countries": set(),
            "count": 0,
            "missing_location_count": 0,
        }
    )

    for row in cert_data:
        key = (row["course_id"], row["y"])
        district_str = f"{int(row['district']):02d}" if row.get("district") else None
        if district_str:
            certs_by_course_year[key]["districts"].add(district_str)
        if row.get("regional"):
            certs_by_course_year[key]["regionals"].add(str(row["regional"]).strip())
        if row.get("province"):
            certs_by_course_year[key]["provinces"].add(str(row["province"]).strip())
        if row.get("country"):
            certs_by_course_year[key]["countries"].add(country_labels.get(row["country"], row["country"]))

        certs_by_course_year[key]["count"] += row["count"]
        if not row.get("district") or not row.get("regional"):
            certs_by_course_year[key]["missing_location_count"] += row["count"]

    for (course_id, year), cert_info in certs_by_course_year.items():
        districts_str = ", ".join(sorted(cert_info["districts"]))
        regionals_str = ", ".join(sorted(cert_info["regionals"]))
        provinces_str = ", ".join(sorted(cert_info["provinces"]))
        countries_str = ", ".join(sorted(cert_info["countries"]))

        report, _created = OnlineCertificateReport.objects.get_or_create(
            course_id=course_id,
            issued_year=year,
            defaults={
                "total_quantity": cert_info["count"],
                "districts_list": districts_str,
                "regional_list": regionals_str,
                "province_list": provinces_str,
                "country_list": countries_str,
                "missing_location_count": cert_info["missing_location_count"],
            },
        )

        if report.sync_enabled and not report.is_closed:
            report.total_quantity = cert_info["count"]
            report.districts_list = districts_str
            report.regional_list = regionals_str
            report.province_list = provinces_str
            report.country_list = countries_str
            report.missing_location_count = cert_info["missing_location_count"]
            report.save(update_fields=[
                "total_quantity",
                "districts_list",
                "regional_list",
                "province_list",
                "country_list",
                "missing_location_count",
                "updated_at",
            ])

    reports = (
        OnlineCertificateReport.objects
        .select_related("course")
        .filter(issued_year__gte=min_year)
        .order_by("-issued_year", "course__title")
    )

    tabs = [("online", "ONLINE")]
    issues_by_cat = {"online": []}
    for report in reports:
        issues_by_cat["online"].append({
            "course": report.course,
            "issued_date": date(report.issued_year, 1, 1),
            "district": report.districts_list or "",
            "regional": report.regional_list or "",
            "province": report.province_list or "",
            "country": report.country_list or "",
            "quantity": 0,
            "impact": report.total_quantity,
            "pct_total": None,
            "prev_year": report.issued_year - 1 if report.issued_year > min_year else min_year,
            "desde_presencial_total": None,
            "desde_online_total": None,
            "image": report.image,
            "note": report.description or "",
            "updated_at": report.updated_at,
            "report_id": report.id,
            "is_online": True,
            "is_closed": report.is_closed,
            "cycle_start_date": report.cycle_start_date,
            "cycle_end_date": report.cycle_end_date,
            "missing_location_count": report.missing_location_count,
        })

    return tabs, dict(issues_by_cat)


PASSING_SCORE = 70
def _passed_quicktest(user, module) -> bool:
    """
    True si el módulo NO tiene QuickTestDefinition,
    o si el usuario tiene un QuickTest con score >= PASSING_SCORE.
    """
    from classroom.quicktest.models import QuickTest, QuickTestDefinition

    has_def = QuickTestDefinition.objects.filter(module=module).exists()
    if not has_def:
        return True

    qt = (
        QuickTest.objects
        .filter(user=user, module=module)
        .order_by("-completed_at", "-id")
        .first()
    )
    if not qt:
        return False

    try:
        return Decimal(str(qt.score)) >= Decimal(str(PASSING_SCORE))
    except Exception:
        return float(qt.score) >= float(PASSING_SCORE)
