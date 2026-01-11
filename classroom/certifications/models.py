# certifications/models.py
from __future__ import annotations

import os
import re
import uuid
from typing import Final

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

_SAFE_COMPONENT_RE: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_component(value: str) -> str:
    value = (value or "").strip()
    value = _SAFE_COMPONENT_RE.sub("_", value)
    value = value.strip("._-")
    return value or "file"

class Certificate(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

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
    cert_no = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    issued_date = models.DateField(default=timezone.now, db_index=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_user_course_certificate")
        ]
        ordering = ("-issued_date",)

    def __str__(self):
        return f"{self.user} | {self.course} | {self.cert_no}"

    @property
    def public_uuid(self) -> str:
        # Some templates expect 'public_uuid'; expose uuid as string for compatibility
        return str(self.uuid)

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
        super().save(*args, **kwargs)
