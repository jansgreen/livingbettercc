import uuid

from django.db import migrations


def ensure_uuid_column(apps, schema_editor):
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
                      AND column_name = 'uuid'
                ) THEN
                    ALTER TABLE certifications_certificate
                    ADD COLUMN uuid uuid;
                END IF;
            END$$;
            """
        )
    else:
        cursor.execute("PRAGMA table_info('certifications_certificate');")
        columns = [row[1] for row in cursor.fetchall()]
        if "uuid" not in columns:
            cursor.execute("ALTER TABLE certifications_certificate ADD COLUMN uuid text;")


def backfill_uuid(apps, schema_editor):
    Certificate = apps.get_model("certifications", "Certificate")

    batch = []
    for cert in Certificate.objects.filter(uuid__isnull=True).iterator(chunk_size=500):
        cert.uuid = uuid.uuid4()
        batch.append(cert)
        if len(batch) >= 500:
            Certificate.objects.bulk_update(batch, ["uuid"])
            batch.clear()
    if batch:
        Certificate.objects.bulk_update(batch, ["uuid"])


def ensure_uuid_constraints(apps, schema_editor):
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
                      AND column_name = 'uuid'
                ) THEN
                    ALTER TABLE certifications_certificate
                    ALTER COLUMN uuid SET NOT NULL;
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
                    WHERE conname = 'certifications_certificate_uuid_key'
                ) THEN
                    ALTER TABLE certifications_certificate
                    ADD CONSTRAINT certifications_certificate_uuid_key UNIQUE(uuid);
                END IF;
            END$$;
            """
        )
    else:
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS certs_cert_uuid_uniq ON certifications_certificate(uuid);"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("certifications", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(ensure_uuid_column, migrations.RunPython.noop),
        migrations.RunPython(backfill_uuid, migrations.RunPython.noop),
        migrations.RunPython(ensure_uuid_constraints, migrations.RunPython.noop),
    ]
