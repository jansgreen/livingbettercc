from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("certifications", "0011_alter_onlinecertificatereport_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="cycle_start_date",
            field=models.DateField(blank=True, null=True, verbose_name="inicio del ciclo"),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="cycle_end_date",
            field=models.DateField(blank=True, null=True, verbose_name="cierre del ciclo"),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="is_closed",
            field=models.BooleanField(db_index=True, default=False, verbose_name="ciclo cerrado"),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="cerrado en"),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="sync_enabled",
            field=models.BooleanField(default=True, verbose_name="sincronizar con certificados"),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="regional_list",
            field=models.TextField(
                blank=True,
                default=None,
                help_text="Lista de regionales que participaron en el curso online.",
                null=True,
                verbose_name="regionales",
            ),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="province_list",
            field=models.TextField(
                blank=True,
                default=None,
                help_text="Lista de provincias que participaron en el curso online.",
                null=True,
                verbose_name="provincias",
            ),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="country_list",
            field=models.TextField(
                blank=True,
                default=None,
                help_text="Lista de paises que participaron en el curso online.",
                null=True,
                verbose_name="paises",
            ),
        ),
        migrations.AddField(
            model_name="onlinecertificatereport",
            name="missing_location_count",
            field=models.PositiveIntegerField(default=0, verbose_name="certificados sin ubicacion completa"),
        ),
    ]
