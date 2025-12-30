from __future__ import annotations

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management.color import no_style
from django.db.utils import ProgrammingError


class Command(BaseCommand):
    help = "Reset database sequences for all models (PostgreSQL)."

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            self.stdout.write(self.style.WARNING("Not a PostgreSQL database; skipping."))
            return

        sql_statements = connection.ops.sequence_reset_sql(no_style(), apps.get_models())
        if not sql_statements:
            self.stdout.write(self.style.WARNING("No sequences to reset."))
            return

        with connection.cursor() as cursor:
            skipped = 0
            for statement in sql_statements:
                try:
                    cursor.execute(statement)
                except ProgrammingError as e:
                    # Some models may exist in INSTALLED_APPS but their tables
                    # are not present in this database (e.g. legacy/optional apps).
                    msg = str(e)
                    if "does not exist" in msg or "UndefinedTable" in msg:
                        skipped += 1
                        continue
                    raise

        reset_count = len(sql_statements) - skipped
        if skipped:
            self.stdout.write(
                self.style.WARNING(
                    f"Reset {reset_count} sequences (skipped {skipped} missing tables)."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"Reset {reset_count} sequences."))
