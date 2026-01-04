import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db import transaction

class Command(BaseCommand):
    help = "Migrates local MEDIA files referenced by ImageFields to Cloudinary (or current DEFAULT storage)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without saving changes."
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of files migrated (0 = no limit)."
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"] or None

        media_root = str(settings.MEDIA_ROOT)
        self.stdout.write(self.style.WARNING(f"MEDIA_ROOT = {media_root}"))
        self.stdout.write(self.style.WARNING(f"DEFAULT storage backend = {settings.STORAGES.get('default', {}).get('BACKEND', 'unknown')}"))

        migrated = 0
        skipped = 0
        missing = 0

        # Recorre TODOS los modelos y busca ImageField / FileField
        for model in apps.get_models():
            fields = []
            for f in model._meta.get_fields():
                # ImageField hereda de FileField
                if getattr(f, "upload_to", None) is not None and f.get_internal_type() in ("ImageField", "FileField"):
                    fields.append(f)

            if not fields:
                continue

            qs = model._default_manager.all().only("pk")
            for obj in qs.iterator(chunk_size=200):
                updated = False

                for f in fields:
                    filefield = getattr(obj, f.name, None)
                    if not filefield:
                        continue

                    name = getattr(filefield, "name", "") or ""
                    if not name:
                        continue

                    # Si ya parece Cloudinary, lo saltamos (heurística simple)
                    # (Cloudinary suele guardar rutas tipo "media/..." igual, así que esto evita doble subida solo si ya está accesible)
                    # Mejor criterio: si storage ya no encuentra local, lo intentamos subir desde MEDIA_ROOT.
                    local_path = os.path.join(media_root, name.replace("/", os.sep))

                    if not os.path.exists(local_path):
                        # Puede que ya esté en storage remoto; si no, lo marcamos missing
                        try:
                            _ = filefield.url  # si existe remoto, no fallará
                            skipped += 1
                            continue
                        except Exception:
                            missing += 1
                            self.stdout.write(self.style.ERROR(f"[MISSING] {model.__name__}(pk={obj.pk}).{f.name} -> {name} (no existe: {local_path})"))
                            continue

                    if dry_run:
                        self.stdout.write(f"[DRY] {model.__name__}(pk={obj.pk}).{f.name} -> subirá {local_path}")
                        migrated += 1
                        if limit and migrated >= limit:
                            self.stdout.write(self.style.SUCCESS("Limit reached (dry-run)."))
                            return
                        continue

                    # Re-subir usando el storage default actual (Cloudinary si está activo)
                    with open(local_path, "rb") as fp:
                        django_file = File(fp)
                        # Guardamos con el mismo nombre relativo, pero esto lo maneja el storage.
                        filefield.save(os.path.basename(local_path), django_file, save=False)

                    updated = True
                    migrated += 1
                    self.stdout.write(self.style.SUCCESS(f"[OK] {model.__name__}(pk={obj.pk}).{f.name} subido"))

                    if limit and migrated >= limit:
                        break

                if updated and not dry_run:
                    with transaction.atomic():
                        obj.save(update_fields=[f.name for f in fields])

                if limit and migrated >= limit:
                    self.stdout.write(self.style.SUCCESS("Limit reached."))
                    return

        self.stdout.write(self.style.SUCCESS(f"Done. migrated={migrated}, skipped={skipped}, missing={missing}"))
