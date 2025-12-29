from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from classroom.certifications.models import InPersonCertificateIssue


@dataclass(frozen=True)
class TaodFromInpersonResult:
    taod_kpis: Dict[str, Any]
    taod_years: List[Dict[str, Any]]


def _pct(part: int, total: int) -> int:
    if total <= 0:
        return 0
    value = int(round((part / total) * 100))
    return max(0, min(100, value))


def get_taod_stats_from_inperson_issues(*, limit_years: int = 6) -> TaodFromInpersonResult:
    """Construye la data que usa el bloque "Impacto TAOD" pero basada en InPersonCertificateIssue.

    Nota: como este modelo es solo "presencial manual", se reporta `online = 0`.
    `impacted` usa `impact` si existe; si no, cae a `quantity`.
    """

    qs = InPersonCertificateIssue.objects.all()
    current_year = timezone.now().year

    totals = qs.aggregate(
        total_quantity=Coalesce(Sum("quantity"), 0),
        total_in_person=Coalesce(Sum("in_person_total"), 0),
        total_impact=Coalesce(Sum("impact"), 0),
    )

    total_quantity = int(totals["total_quantity"] or 0)
    total_in_person = int(totals["total_in_person"] or 0)
    total_impact = int(totals["total_impact"] or 0)

    current_year_totals = qs.filter(issued_date__year=current_year).aggregate(
        total_quantity=Coalesce(Sum("quantity"), 0),
        total_in_person=Coalesce(Sum("in_person_total"), 0),
        total_impact=Coalesce(Sum("impact"), 0),
    )
    current_year_total = int(current_year_totals["total_quantity"] or 0)

    # En este modo, "TAOD" se interpreta como totales manuales cargados en el modelo.
    taod_kpis = {
        "current_year": current_year,
        "total": total_quantity,
        "current_year_total": current_year_total,
        "online": 0,
        "in_person": total_in_person,
        "impacted": total_impact if total_impact > 0 else total_quantity,
    }

    year_rows = list(
        qs.values("issued_date__year")
        .annotate(
            total_quantity=Coalesce(Sum("quantity"), 0),
            total_in_person=Coalesce(Sum("in_person_total"), 0),
            total_impact=Coalesce(Sum("impact"), 0),
        )
        .order_by("-issued_date__year")
    )

    year_rows = [r for r in year_rows if r.get("issued_date__year") is not None][: max(0, limit_years)]

    max_total = 0
    for r in year_rows:
        max_total = max(max_total, int(r.get("total_quantity") or 0))

    # Pre-cargar imagen/nota "representativa" por año (la última con contenido)
    by_year_latest = (
        qs.exclude(image="")
        .exclude(image__isnull=True)
        .order_by("-issued_date", "-updated_at")
    )

    years: List[Dict[str, Any]] = []
    for r in year_rows:
        year = int(r["issued_date__year"])
        total = int(r.get("total_quantity") or 0)
        in_person = int(r.get("total_in_person") or 0)
        impact = int(r.get("total_impact") or 0)
        online = 0

        impacted = impact if impact > 0 else total

        pct_total = int(round((total / max_total) * 100)) if max_total else 0
        pct_total = max(0, min(100, pct_total))
        if total > 0 and pct_total == 0:
            pct_total = 1

        pct_online = _pct(online, total)
        pct_in_person = _pct(in_person, total)

        image_url: Optional[str] = None
        note: str = ""

        # Imagen: la última del año si existe
        img_obj = by_year_latest.filter(issued_date__year=year).first()
        if img_obj and getattr(img_obj, "image", None):
            try:
                image_url = img_obj.image.url
            except Exception:
                image_url = None

        # Nota: la última nota no vacía del año
        note_obj = (
            qs.exclude(note="")
            .order_by("-issued_date", "-updated_at")
            .filter(issued_date__year=year)
            .first()
        )
        if note_obj and getattr(note_obj, "note", None):
            note = str(note_obj.note)

        years.append(
            {
                "year": year,
                "total": total,
                "online": online,
                "in_person": in_person,
                "impacted": impacted,
                "pct_total": pct_total,
                "pct_online": pct_online,
                "pct_in_person": pct_in_person,
                "image_url": image_url,
                "notes": note,
            }
        )

    return TaodFromInpersonResult(taod_kpis=taod_kpis, taod_years=years)
