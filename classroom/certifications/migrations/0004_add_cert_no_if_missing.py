import re
from django.db import migrations, transaction
from django.utils import timezone


def ensure_cert_no_column(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()

    if vendor == "postgresql":
        cursor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'certifications_certificate'
                      AND column_name = 'cert_no'
                ) THEN
                    ALTER TABLE certifications_certificate
                    ADD COLUMN cert_no varchar(30);
                END IF;
            END$$;
            """
        )
    else:
        cursor.execute("PRAGMA table_info('certifications_certificate');")
        columns = [row[1] for row in cursor.fetchall()]
        if "cert_no" not in columns:
            cursor.execute("ALTER TABLE certifications_certificate ADD COLUMN cert_no varchar(30);")


def backfill_cert_no(apps, schema_editor):
    Certificate = apps.get_model("certifications", "Certificate")
    pattern = re.compile(r"LBCC-(\d{4})-(\d+)$")
    counters = {}
    updated = []

    with transaction.atomic():
        qs = (
            Certificate.objects
            .select_for_update()
            .order_by("issued_date", "id")
        )

        for cert in qs.iterator(chunk_size=500):
            existing = (cert.cert_no or "").strip()
            if existing:
                match = pattern.match(existing)
                if match:
                    year = int(match.group(1))
                    seq = int(match.group(2))
                    counters[year] = max(counters.get(year, 0), seq)
                continue

            year = cert.issued_date.year if cert.issued_date else timezone.now().year
            next_seq = counters.get(year, 0) + 1
            counters[year] = next_seq
            cert.cert_no = f"LBCC-{year}-{next_seq:06d}"
            updated.append(cert)

            if len(updated) >= 500:
                Certificate.objects.bulk_update(updated, ["cert_no"])
                updated.clear()

        if updated:
            Certificate.objects.bulk_update(updated, ["cert_no"])


def ensure_cert_no_constraints(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()

    if vendor == "postgresql":
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'certifications_certificate'
                      AND column_name = 'cert_no'
                ) THEN
                    ALTER TABLE certifications_certificate
                    ALTER COLUMN cert_no SET NOT NULL;
                END IF;
            END$$;
            """
        )
        cursor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'certifications_certificate_cert_no_key'
                ) THEN
                    ALTER TABLE certifications_certificate
                    ADD CONSTRAINT certifications_certificate_cert_no_key UNIQUE(cert_no);
                END IF;
            END$$;
            """
        )
    else:
        # SQLite: aplica índice único; la columna ya está poblada por backfill.
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS certs_cert_no_uniq ON certifications_certificate(cert_no);"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("certifications", "0003_alter_certificate_uuid"),
    ]

    operations = [
        migrations.RunPython(ensure_cert_no_column, migrations.RunPython.noop),
        migrations.RunPython(backfill_cert_no, migrations.RunPython.noop),
        migrations.RunPython(ensure_cert_no_constraints, migrations.RunPython.noop),
    ]
