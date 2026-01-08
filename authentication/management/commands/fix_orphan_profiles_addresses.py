from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = "Null out orphaned Profiles.direccion references to non-existent Address rows. Safe pre-migration cleanup."

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            from authentication.models.profiles import Profiles
            from authentication.address.models import Address
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Import error: {e}"))
            return

        valid_ids = set(Address.objects.values_list('id', flat=True))
        orphans = Profiles.objects.filter(direccion_id__isnull=False).exclude(direccion_id__in=valid_ids)
        count = orphans.count()
        if count:
            orphans.update(direccion=None)
        self.stdout.write(self.style.SUCCESS(f"Orphaned profiles fixed: {count}"))