from django.core.management.base import BaseCommand
from django.db import connection, transaction
from datetime import datetime

from home.models import ReportActivity
from classroom.courses.models import Course


LEGACY_TABLE = "certifications_inpersoncertificateissue"


def table_exists(table_name: str) -> bool:
    try:
        return table_name in connection.introspection.table_names()
    except Exception:
        # Fallback for older/introspection issues
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    [table_name],
                )
                return cursor.fetchone() is not None
            except Exception:
                return False


class Command(BaseCommand):
    help = (
        "Migrate legacy InPersonCertificateIssue rows into ReportActivity using only overlapping fields, "
        "then optionally drop the legacy table."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Do not write changes, only report.")
        parser.add_argument(
            "--skip-drop",
            action="store_true",
            help="Do not drop the legacy table after migration.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        skip_drop = options.get("skip_drop", False)

        if not table_exists(LEGACY_TABLE):
            self.stdout.write(self.style.WARNING(f"Legacy table '{LEGACY_TABLE}' not found. Nothing to migrate."))
            return

        self.stdout.write(self.style.NOTICE(f"Found legacy table '{LEGACY_TABLE}'. Starting migration..."))

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT course_id, issued_date, district, quantity, image, note FROM {LEGACY_TABLE}"
            )
            rows = cursor.fetchall()

        total_rows = len(rows)
        created_count = 0
        updated_count = 0
        skipped_count = 0

        if dry_run:
            self.stdout.write(self.style.NOTICE(f"Dry run: {total_rows} rows would be processed."))
            return

        with transaction.atomic():
            for (course_id, issued_date, district, quantity, image, note) in rows:
                try:
                    # Parse year from date string (YYYY-MM-DD) or datetime
                    if isinstance(issued_date, datetime):
                        issued_year = issued_date.year
                    else:
                        # Expect str in sqlite
                        issued_year = datetime.fromisoformat(str(issued_date)).year
                except Exception:
                    # Fallback: skip if date invalid
                    skipped_count += 1
                    continue

                try:
                    course = Course.objects.get(pk=course_id)
                except Course.DoesNotExist:
                    skipped_count += 1
                    continue

                defaults = {
                    "quantity": int(quantity or 0),
                    "description": (note or None),
                }
                # Image path may map if the storage path is compatible
                try:
                    if image:
                        defaults["image"] = image
                except Exception:
                    pass

                obj, created = ReportActivity.objects.get_or_create(
                    course=course,
                    issued_year=int(issued_year),
                    district=(district or "").strip(),
                    defaults=defaults,
                )

                if created:
                    created_count += 1
                else:
                    # If exists, aggregate quantities & merge description when missing
                    prev_qty = int(obj.quantity or 0)
                    add_qty = int(quantity or 0)
                    new_qty = prev_qty + add_qty
                    # Only append description if provided and different
                    new_desc = obj.description
                    if note and (not new_desc or note not in (new_desc or "")):
                        new_desc = ((new_desc or "") + "\n" + str(note)).strip()

                    # Keep first non-empty image
                    if image and not obj.image:
                        obj.image = image

                    obj.quantity = new_qty
                    obj.description = new_desc
                    obj.save(update_fields=["quantity", "description", "image"])
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Migration completed. Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}."
            )
        )

        if not skip_drop:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DROP TABLE {LEGACY_TABLE}")
                self.stdout.write(self.style.SUCCESS(f"Dropped legacy table '{LEGACY_TABLE}'."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to drop legacy table: {e}"))
