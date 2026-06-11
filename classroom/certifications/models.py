# certifications/models.py
from __future__ import annotations

import os
import re
import uuid as uuid_module
from typing import Final

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


def current_year():
    return timezone.now().year

_SAFE_COMPONENT_RE: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_component(value: str) -> str:
    value = (value or "").strip()
    value = _SAFE_COMPONENT_RE.sub("_", value)
    value = value.strip("._-")
    return value or "file"

class Certificate(models.Model):
    uuid = models.UUIDField(default=uuid_module.uuid4, unique=True, editable=False, db_index=True)
    public_uuid = models.UUIDField(default=uuid_module.uuid4, unique=True, editable=False, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    pending = models.BooleanField(default=False, db_index=True)
    cert_no = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    certificate_number = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    issued_date = models.DateField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_user_course_certificate")
        ]
        ordering = ("-issued_date",)

    def __str__(self):
        return f"{self.user} | {self.course} | {self.cert_no}"

    def _generate_cert_no(self):
        year = (self.issued_date.year if self.issued_date else timezone.now().year)
        prefix = f"LBCC-{year}-"

        with transaction.atomic():
            last = (
                Certificate.objects
                .select_for_update()
                .filter(cert_no__startswith=prefix)
                .order_by("-cert_no")
                .first()
            )

            if last and last.cert_no.startswith(prefix):
                try:
                    last_num = int(last.cert_no.replace(prefix, ""))
                except ValueError:
                    last_num = 0
            else:
                last_num = 0

            next_num = last_num + 1
            return f"{prefix}{next_num:06d}"

    def save(self, *args, **kwargs):
        if not self.cert_no:
            self.cert_no = self._generate_cert_no()
        if not self.certificate_number:
            self.certificate_number = self.cert_no
        super().save(*args, **kwargs)

class BecadoCertificateRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        AUTHORIZED = "authorized", "Autorizado"

    certificate = models.OneToOneField(
        Certificate,
        on_delete=models.CASCADE,
        related_name="becado_request",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="becado_certificate_requests",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="becado_certificate_requests",
    )
    full_name = models.CharField(max_length=180)
    educational_center = models.CharField(max_length=200)
    regional = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)
    authorized_at = models.DateTimeField(null=True, blank=True, db_index=True)
    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authorized_becado_certificate_requests",
    )

    class Meta:
        ordering = ("-sent_at",)

    def __str__(self):
        return f"{self.full_name} | {self.course} | {self.status}"

class OnlineCertificateReport(models.Model):
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="online_certificate_reports",
        verbose_name="curso",
    )

    issued_year = models.PositiveIntegerField(
        default=current_year,
        db_index=True,
        verbose_name="año",
    )

    total_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="cantidad total de certificados online",
    )

    districts_list = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name="distritos/regionales",
        help_text="Lista de distritos separados por comas: 01, 05, 06, 07, 15, 11, 13, 16",
    )

    image = models.ImageField(
        upload_to="certifications/online_reports/",
        blank=True,
        null=True,
        verbose_name="imagen",
    )

    description = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name="descripción",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="creado",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="actualizado",
    )

    class Meta:
        ordering = ("-issued_year", "course")
        constraints = [
            models.UniqueConstraint(
                fields=["course", "issued_year"],
                name="unique_online_certificate_report",
            ),
        ]
        verbose_name = "Reporte de Certificado Online"
        verbose_name_plural = "Reportes de Certificados Online"

    def __str__(self):
        return f"{self.course} | {self.issued_year} | {self.total_quantity}"

    @property
    def missing_fields(self):
        missing = []
        if not self.issued_year:
            missing.append("año")
        if not self.districts_list:
            missing.append("distritos/regionales")
        if not self.description:
            missing.append("descripción")
        if not self.image:
            missing.append("imagen")
        return missing

    @property
    def has_missing_fields(self):
        return bool(self.missing_fields)
