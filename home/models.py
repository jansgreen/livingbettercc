# certifications/models.py
from django.db import models
from django.utils import timezone


def current_year():
    return timezone.now().year


class ReportActivity(models.Model):
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="report_activities",
        verbose_name="curso",
    )

    issued_year = models.PositiveIntegerField(
        default=current_year,
        db_index=True,
        verbose_name="año",
    )

    district = models.CharField(
        max_length=120,
        db_index=True,
        verbose_name="distrito / regional",
    )

    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="cantidad presencial",
    )

    # opcional: evidencia / acta / foto del evento
    image = models.ImageField(
        upload_to="certifications/report_activities/",
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
        ordering = ("-issued_year", "district")
        constraints = [
            models.UniqueConstraint(
                fields=["course", "issued_year", "district"],
                name="unique_reportactivity_course_year_district",
            ),
        ]
        verbose_name = "Actividad de Reporte"
        verbose_name_plural = "Actividades de Reportes"

    def __str__(self):
        return f"{self.course} | {self.issued_year} | {self.district} | {self.quantity}"
