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
from home.models import ReportActivity  # ajusta al path real
from decimal import Decimal


def _clamp_pct(v: int) -> int:
    return max(0, min(100, int(v)))

def get_report_activity_grouped_for_tabs(*, limit_years: int = 6) -> Tuple[List[Tuple[str, str]], Dict[str, List[Dict[str, Any]]]]:
    """
    Tabs por curso.
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
        .select_related("course")
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

    # Tabs: cursos que tengan presencial o digital
    course_map: Dict[int, Any] = {}

    for ra in ra_qs:
        if ra.course_id:
            course_map[ra.course_id] = ra.course

    for (course_id, _year), _total in digital_by_course_year.items():
        if course_id not in course_map:
            # Para no hacer query por cada uno, buscamos un certificado cualquiera del curso
            c = Certificate.objects.filter(course_id=course_id).select_related("course").first()
            if c:
                course_map[course_id] = c.course

    # Orden de tabs por nombre de curso
    courses = sorted(course_map.values(), key=lambda x: (x.title or "").lower())

    tabs: List[Tuple[str, str]] = [(str(c.id), c.title) for c in courses]
    issues_by_cat: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    # Precálculo: totales acumulados por curso/año
    presencial_sum_by_course_year = defaultdict(int)
    for ra in ra_qs:
        presencial_sum_by_course_year[(ra.course_id, ra.issued_year)] += int(ra.quantity or 0)

    # Helper: acumulado desde prev_year
    def sum_presencial_desde(course_id: int, start_year: int) -> int:
        return sum(v for (cid, y), v in presencial_sum_by_course_year.items() if cid == course_id and y >= start_year)

    def sum_digital_desde(course_id: int, start_year: int) -> int:
        return sum(v for (cid, y), v in digital_by_course_year.items() if cid == course_id and y >= start_year)

    # Para cada curso/tab, creamos items por ReportActivity
    # Y añadimos digital en el mismo “impact row”
    for course in courses:
        tab_id = str(course.id)

        # group presencial rows by year
        pres_rows = [ra for ra in ra_qs if ra.course_id == course.id]
        years_present = sorted({ra.issued_year for ra in pres_rows}, reverse=True)

        # si hay digital y no hay presencial en ese año, igual queremos mostrar el año
        digital_years = sorted({y for (cid, y), v in digital_by_course_year.items() if cid == course.id and v > 0}, reverse=True)

        all_years = sorted(set(years_present) | set(digital_years), reverse=True)[:max(1, limit_years)]

        # para pct_total (relativo al máximo de ese curso)
        max_total_for_course = 0
        totals_for_course_year = {}
        for y in all_years:
            pres_total = int(presencial_sum_by_course_year.get((course.id, y), 0))
            dig_total = int(digital_by_course_year.get((course.id, y), 0))
            tot = pres_total + dig_total
            totals_for_course_year[y] = tot
            max_total_for_course = max(max_total_for_course, tot)

        # Creamos una fila por año.
        # Si hay varios distritos en el mismo año, se muestran como filas separadas, pero con el mismo digital.
        # (Esto se ajusta perfecto a tu template actual)
        for y in all_years:
            rows_this_year = [ra for ra in pres_rows if ra.issued_year == y]

            # Si no hay presencial ese año, creamos un “row virtual” para mostrar digital.
            if not rows_this_year:
                rows_this_year = [None]

            for ra in rows_this_year:
                presencial_qty = int(getattr(ra, "quantity", 0) or 0)
                digital_qty = int(digital_by_course_year.get((course.id, y), 0))

                total_year = int(totals_for_course_year.get(y, presencial_qty + digital_qty))
                pct_total = 0
                if max_total_for_course > 0:
                    pct_total = int(round((total_year / max_total_for_course) * 100))
                    pct_total = _clamp_pct(pct_total)
                    if total_year > 0 and pct_total == 0:
                        pct_total = 1

                prev_year = y  # para tu texto “desde”
                desde_pres = sum_presencial_desde(course.id, prev_year)
                desde_dig = sum_digital_desde(course.id, prev_year)

                issues_by_cat[tab_id].append(
                    {
                        "course": course,
                        # para filtros date del template
                        "issued_date": date(y, 1, 1),
                        "district": getattr(ra, "district", "—") if ra else "—",
                        # tu template:
                        "quantity": presencial_qty,   # Presencial
                        "impact": digital_qty,        # Online/Digital
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
