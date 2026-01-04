from __future__ import annotations

import os
import re
import uuid
from typing import Final

from django.conf import settings
from django.db import models
from django.utils import timezone

try:
    from django_ckeditor_5.fields import CKEditor5Field
except Exception:  # pragma: no cover
    CKEditor5Field = None  # type: ignore


_SAFE_COMPONENT_RE: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_component(value: str) -> str:
    value = (value or "").strip()
    value = _SAFE_COMPONENT_RE.sub("_", value)
    value = value.strip("._-")
    return value or "file"


def certificate_upload_to(instance: "Certificate", filename: str) -> str:
    ext = os.path.splitext(filename)[1] or ".pdf"
    cert_no = _safe_component(getattr(instance, "certificate_number", "certificate"))
    return f"certificates/pdfs/{cert_no}{ext}" 


def in_person_issue_image_upload_to(instance: "InPersonCertificateIssue", filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    district = _safe_component(getattr(instance, "district", "district"))
    course_id = getattr(instance, "course_id", None) or "course"
    issued_date = getattr(instance, "issued_date", None)
    date_part = issued_date.isoformat() if issued_date else "date"
    return f"certificates/in_person/{course_id}/{date_part}/{district}{ext}" 


class Certificate(models.Model):
    public_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    certificate_number = models.CharField(max_length=64, unique=True, default="TEMP-CERT")
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificates",
        default=1,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        default=1,
    )
    issued_date = models.DateField(default=timezone.now)
    pdf_file = models.FileField(upload_to=certificate_upload_to, blank=True, null=True)

    class Meta:
        ordering = ["-issued_date"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.certificate_number}"

class InPersonCertificateIssue(models.Model):
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="in_person_issues",
    )
    category = models.ForeignKey(
        "certifications.InPersonCategory",
        on_delete=models.SET_NULL,
        related_name="issues",
        blank=True,
        null=True,
    )
    issued_date = models.DateField(default=timezone.now, db_index=True)
    district = models.CharField(max_length=120, db_index=True)

    quantity = models.PositiveIntegerField(default=0)
    in_person_total = models.PositiveIntegerField(default=0)
    impact = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to=in_person_issue_image_upload_to, blank=True, null=True)

    if CKEditor5Field is not None:
        note = CKEditor5Field(blank=True, max_length=255)
    else:
        note = models.TextField(blank=True, max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="in_person_certificate_issues",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_date", "course__title", "district"]
        constraints = [
            models.UniqueConstraint(
                fields=("course", "issued_date", "district", "category"),
                name="uniq_inperson_course_date_district",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.course_id} {self.issued_date} {self.district}"

class InPersonCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name