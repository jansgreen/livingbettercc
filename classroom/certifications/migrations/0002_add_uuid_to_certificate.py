import uuid

from django.db import migrations, models


def backfill_uuid(apps, schema_editor):
    Certificate = apps.get_model("certifications", "Certificate")
    qs = Certificate.objects.filter(uuid__isnull=True).only("id")

    batch = []
    for cert in qs.iterator(chunk_size=1000):
        cert.uuid = uuid.uuid4()
        batch.append(cert)
        if len(batch) >= 1000:
            Certificate.objects.bulk_update(batch, ["uuid"])
            batch.clear()
    if batch:
        Certificate.objects.bulk_update(batch, ["uuid"])


class Migration(migrations.Migration):
    dependencies = [
        ("certifications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="certificate",
            name="uuid",
            field=models.UUIDField(
                null=True, unique=True, editable=False, db_index=True
            ),
        ),
        migrations.RunPython(backfill_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="certificate",
            name="uuid",
            field=models.UUIDField(
                null=False, unique=True, editable=False, db_index=True
            ),
        ),
    ]
