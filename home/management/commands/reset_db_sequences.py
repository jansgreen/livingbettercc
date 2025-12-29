from __future__ import annotations

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management.color import no_style


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
            for statement in sql_statements:
                cursor.execute(statement)

        self.stdout.write(self.style.SUCCESS(f"Reset {len(sql_statements)} sequences."))
