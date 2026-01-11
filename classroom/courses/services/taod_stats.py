# classroom/courses/services/taod_status.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.db.models import IntegerField
from django.db.models.functions import ExtractYear
from django.utils import timezone

from classroom.certifications.models import Certificate
from classroom.courses.models import Course, Program

from home.models import ReportActivity

TAOD_PROGRAM_NAME = "TAOD"


@dataclass(frozen=True)
class TaodStatsResult:
    taod_kpis: dict[str, int]
    taod_years: list[dict[str, Any]]
    top_courses: list[dict[str, Any]]


def _clamp_pct(v: int) -> int:
    return max(0, min(100, int(v)))


def get_taod_stats(*, top_n: int = 10, limit_years: int = 6) -> TaodStatsResult:
    """
    TAOD impact stats basados en:
      - Online: Certificate (count por año)
      - Presencial: ReportActivity (sum quantity por año)
      - Imagen/nota representativa por año: desde ReportActivity (última con image/description)
    """

    current_year = int(timezone.now().year)
    min_year = current_year - max(0, int(limit_years) - 1)

    program = Program.objects.filter(name=TAOD_PROGRAM_NAME).first()
    if not program:
        return TaodStatsResult(
            taod_kpis={
                "total": 0,
                "current_year_total": 0,
                "online": 0,
                "in_person": 0,
                "current_year": current_year,
            },
            taod_years=[],
            top_courses=[],
        )

    # Cursos TAOD (para filtrar ReportActivity también)
    taod_course_ids = list(
        Course.objects.filter(program=program).values_list("id", flat=True)
    )

    # -----------------------
    # ONLINE (Certificate)
    # -----------------------
    online_rows = (
        Certificate.objects
        .filter(course__program=program, issued_date__isnull=False)
        .filter(issued_date__year__gte=min_year)
        .annotate(y=ExtractYear("issued_date"))
        .values("y")
        .annotate(online=Count("id"))
        .order_by("-y")
    )

    online_by_year: dict[int, int] = {}
    for row in online_rows:
        y = row.get("y")
        if y is None:
            continue
        online_by_year[int(y)] = int(row.get("online") or 0)

    # -----------------------
    # IN-PERSON (ReportActivity)
    # -----------------------
    inperson_rows = (
        ReportActivity.objects
        .filter(course_id__in=taod_course_ids)
        .filter(issued_year__gte=min_year)
        .values("issued_year")
        .annotate(in_person=Coalesce(Sum("quantity"), 0))
        .order_by("-issued_year")
    )

    in_person_by_year: dict[int, int] = {}
    for row in inperson_rows:
        y = row.get("issued_year")
        if y is None:
            continue
        in_person_by_year[int(y)] = int(row.get("in_person") or 0)

    # -----------------------
    # Imagen/nota representativa por año (última por issued_year)
    # -----------------------
    image_by_year: dict[int, str] = {}
    note_by_year: dict[int, str] = {}

    rep_qs = (
        ReportActivity.objects
        .filter(course_id__in=taod_course_ids)
        .filter(issued_year__gte=min_year)
        .order_by("-issued_year", "-created_at", "-id")
    )

    for obj in rep_qs:
        y = int(obj.issued_year)
        if y not in image_by_year:
            if getattr(obj, "image", None):
                try:
                    image_by_year[y] = obj.image.url
                except Exception:
                    image_by_year[y] = ""
            else:
                image_by_year[y] = ""

        if y not in note_by_year:
            note_by_year[y] = str(obj.description or "")

        # si ya tenemos ambos para ese año, seguimos
        if y in image_by_year and y in note_by_year:
            continue

    # -----------------------
    # Merge años
    # -----------------------
    years = sorted(
        set(online_by_year.keys()) | set(in_person_by_year.keys()),
        reverse=True
    )

    taod_years: list[dict[str, Any]] = []
    for y in years:
        online = int(online_by_year.get(y, 0))
        in_person = int(in_person_by_year.get(y, 0))

        taod_years.append(
            {
                "year": int(y),
                "online": online,
                "in_person": in_person,
                "total": online + in_person,
                "impacted": 0,  # si luego quieres estimaciones, lo añadimos aquí
                "notes": note_by_year.get(int(y), ""),
                "image_url": image_by_year.get(int(y), ""),
            }
        )

    # % bars
    max_year_total = max((int(r["total"]) for r in taod_years), default=0)
    for r in taod_years:
        total = int(r["total"])
        online = int(r["online"])
        in_person = int(r["in_person"])

        r["pct_total"] = int(round((total / max_year_total) * 100)) if max_year_total else 0
        r["pct_total"] = _clamp_pct(r["pct_total"])
        if total:
            r["pct_online"] = _clamp_pct(int(round((online / total) * 100)))
            r["pct_in_person"] = _clamp_pct(100 - int(r["pct_online"]))
        else:
            r["pct_online"] = 0
            r["pct_in_person"] = 0

    # YoY change (lista desc)
    for i, r in enumerate(taod_years):
        prev = taod_years[i + 1] if i + 1 < len(taod_years) else None
        r["prev_year"] = int(prev["year"]) if prev else None
        if not prev:
            r["delta_total"] = 0
            r["pct_change_total"] = 0
            continue

        delta = int(r["total"]) - int(prev["total"])
        r["delta_total"] = int(delta)
        prev_total = int(prev["total"])
        r["pct_change_total"] = int(round((delta / prev_total) * 100)) if prev_total else 0

    # KPIs
    online_total = sum(int(r["online"]) for r in taod_years)
    in_person_total = sum(int(r["in_person"]) for r in taod_years)
    total_all = sum(int(r["total"]) for r in taod_years)

    current_year_row = next((r for r in taod_years if int(r["year"]) == current_year), None)
    current_year_total = int(current_year_row["total"]) if current_year_row else 0

    # -----------------------
    # Top courses (solo TAOD o global)
    # Aquí lo haré TAOD por coherencia.
    # -----------------------
    top_qs = (
        Course.objects.filter(program=program, published=True)
        .annotate(
            online_certified_count=Count("certificates", distinct=True),
        )
        .order_by("-online_certified_count", "title")
    )

    top_courses_raw = list(top_qs[: max(1, int(top_n))])
    top_total = int(top_courses_raw[0].online_certified_count) if top_courses_raw else 0

    top_courses: list[dict[str, Any]] = []
    for c in top_courses_raw:
        total = int(c.online_certified_count or 0)
        percent = int(round((total / top_total) * 100)) if top_total else 0
        top_courses.append(
            {
                "pk": c.pk,
                "title": c.title,
                "certified_total": total,
                "blurb": c.description,
                "percent": _clamp_pct(percent),
            }
        )

    return TaodStatsResult(
        taod_kpis={
            "total": int(total_all),
            "current_year_total": int(current_year_total),
            "online": int(online_total),
            "in_person": int(in_person_total),
            "current_year": int(current_year),
        },
        taod_years=taod_years,
        top_courses=top_courses,
    )
