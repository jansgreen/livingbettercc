from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef


class Command(BaseCommand):
    help = "List Profiles with direccion_id set to non-existent Address rows. Does not modify data."

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=50, help='Max rows to display')

    def handle(self, *args, **options):
        try:
            from authentication.models.profiles import Profiles
            from authentication.address.models import Address
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Import error: {e}"))
            return

        limit = options['limit']
        invalid_qs = (
            Profiles.objects
            .filter(direccion_id__isnull=False)
            .annotate(has_addr=Exists(Address.objects.filter(pk=OuterRef('direccion_id'))))
            .filter(has_addr=False)
        )

        count = invalid_qs.count()
        self.stdout.write(self.style.WARNING(f"Orphaned profiles found: {count}"))

        for pid, uid, did in invalid_qs.values_list('id', 'user_id', 'direccion_id')[:limit]:
            self.stdout.write(f"id={pid} user_id={uid} direccion_id={did}")
