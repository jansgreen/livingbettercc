from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from classroom.certifications.models import Certificate, InPersonCertificateIssue
from classroom.courses.models import Course, Program, ProgramYearStat


TAOD_PROGRAM_NAME = "TAOD"


@dataclass(frozen=True)
class TaodStatsResult:
    taod_kpis: dict[str, int]
    taod_years: list[dict[str, Any]]
    top_courses: list[dict[str, Any]]


def get_taod_stats(*, top_n: int = 10) -> TaodStatsResult:
    """Compute TAOD impact stats from Certificates + manual in-person per year.

    Online certificates are authoritative from Certificate rows.
    Presencial / impacted / notes come from ProgramYearStat.
    """

    current_year = timezone.now().year

    program = Program.objects.filter(name=TAOD_PROGRAM_NAME).first()
    if not program:
        return TaodStatsResult(
            taod_kpis={
                "total": 0,
                "current_year_total": 0,
                "online": 0,
                "in_person": 0,
                "current_year": int(current_year),
            },
            taod_years=[],
            top_courses=[],
        )

    # --- TAOD online counts by year ---
    online_rows = (
        Certificate.objects.filter(course__program=program)
        .exclude(issued_date__isnull=True)
        .values("issued_date__year")
        .annotate(online=Count("id"))
    )
    online_by_year: dict[int, int] = {}
    for row in online_rows:
        year = row.get("issued_date__year")
        if year is None:
            continue
        online_by_year[int(year)] = int(row["online"])

    # --- TAOD in-person (presencial) by year from district entries ---
    in_person_rows = (
        InPersonCertificateIssue.objects.filter(course__program=program)
        .exclude(issued_date__isnull=True)
        .values('issued_date__year')
        .annotate(in_person=Coalesce(Sum('quantity'), 0))
    )
    in_person_by_year: dict[int, int] = {}
    for row in in_person_rows:
        year = row.get('issued_date__year')
        if year is None:
            continue
        in_person_by_year[int(year)] = int(row.get('in_person') or 0)

    # --- Representative image per year (latest uploaded in-person image for that year) ---
    image_by_year: dict[int, str] = {}
    for issue in (
        InPersonCertificateIssue.objects.filter(course__program=program)
        .exclude(issued_date__isnull=True)
        .exclude(image__isnull=True)
        .exclude(image='')
        .order_by('-issued_date', '-updated_at', '-id')
    ):
        year = getattr(issue.issued_date, 'year', None)
        if not year or int(year) in image_by_year:
            continue
        try:
            image_by_year[int(year)] = issue.image.url
        except Exception:
            image_by_year[int(year)] = ''

    # --- TAOD manual impacted / notes by year ---
    manual_rows = ProgramYearStat.objects.filter(program=program)
    manual_by_year: dict[int, ProgramYearStat] = {int(r.year): r for r in manual_rows}

    years = sorted(set(online_by_year.keys()) | set(in_person_by_year.keys()) | set(manual_by_year.keys()), reverse=True)

    taod_years: list[dict[str, Any]] = []
    for year in years:
        online = int(online_by_year.get(year, 0))
        manual = manual_by_year.get(year)
        # Prefer district-based in-person entries when present for that year; else fallback to legacy ProgramYearStat.in_person_certified
        if year in in_person_by_year:
            in_person = int(in_person_by_year.get(year, 0))
        else:
            in_person = int(manual.in_person_certified) if manual else 0
        impacted = int(manual.estimated_children_impacted) if manual else 0
        notes = str(manual.notes) if (manual and manual.notes) else ""

        taod_years.append(
            {
                "year": int(year),
                "online": online,
                "in_person": in_person,
                "total": online + in_person,
                "impacted": impacted,
                "notes": notes,
                "image_url": image_by_year.get(int(year), ''),
            }
        )

    max_year_total = max((y["total"] for y in taod_years), default=0)
    for y in taod_years:
        total = int(y["total"])
        online = int(y["online"])
        in_person = int(y["in_person"])

        y["pct_total"] = int(round((total / max_year_total) * 100)) if max_year_total else 0
        if total:
            y["pct_online"] = int(round((online / total) * 100))
            y["pct_in_person"] = max(0, 100 - int(y["pct_online"]))
        else:
            y["pct_online"] = 0
            y["pct_in_person"] = 0

    # Year-over-year change (compare to next item, since list is sorted desc)
    for i, y in enumerate(taod_years):
        prev = taod_years[i + 1] if i + 1 < len(taod_years) else None
        y["prev_year"] = int(prev["year"]) if prev else None
        if not prev:
            y["delta_total"] = 0
            y["pct_change_total"] = 0
            continue

        delta = int(y["total"]) - int(prev["total"])
        y["delta_total"] = int(delta)
        prev_total = int(prev["total"])
        if prev_total:
            y["pct_change_total"] = int(round((delta / prev_total) * 100))
        else:
            y["pct_change_total"] = 0

    online_total = sum(y["online"] for y in taod_years)
    in_person_total = sum(y["in_person"] for y in taod_years)
    total_all = sum(y["total"] for y in taod_years)

    current_year_row = next((y for y in taod_years if y["year"] == int(current_year)), None)
    current_year_total = int(current_year_row["total"]) if current_year_row else 0

    # --- Top courses (overall, not only TAOD) ---
    top_qs = (
        Course.objects.filter(published=True)
        .annotate(
            online_certified_count=Count("certificates", distinct=True),
            total_certified_count=(
                Coalesce(F("manual_certified_add"), 0)
                + Coalesce(Sum("year_stats__manual_certified_add"), 0)
                + Count("certificates", distinct=True)
            ),
        )
        .order_by("-total_certified_count", "title")
    )

    top_courses_raw = list(top_qs[: max(1, int(top_n))])
    top_total = int(top_courses_raw[0].certified_total) if top_courses_raw else 0

    top_courses: list[dict[str, Any]] = []
    for course in top_courses_raw:
        total = int(course.certified_total)
        percent = int(round((total / top_total) * 100)) if top_total else 0
        top_courses.append(
            {
                "pk": course.pk,
                "title": course.title,
                "certified_total": total,
                "manual_certified_add": int(course.manual_certified_add or 0),
                "blurb": course.description,
                "percent": max(0, min(100, percent)),
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
