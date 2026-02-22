from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Merge legacy student groups into 'estudiantes' group, reassign users, and delete old groups."

    def handle(self, *args, **options):
        old_group = Group.objects.filter(name__in=['students', 'student', 'estudiante']).first()
        new_group, _ = Group.objects.get_or_create(name='estudiantes')

        if not old_group:
            self.stdout.write(self.style.NOTICE("No existen grupos legacy de estudiantes. Ninguna acción necesaria."))
            return

        users = list(old_group.user_set.all())
        if not users:
            # no users, safe to delete
            old_group.delete()
            self.stdout.write(self.style.SUCCESS("Grupo legacy eliminado (estaba vacío)."))
            return

        migrated = 0
        for u in users:
            # Add to new group (idempotente)
            new_group.user_set.add(u)
            migrated += 1
            self.stdout.write(f"Movido usuario: {u.username}")

        # After reassigning users, delete the old group
        old_group.delete()
        self.stdout.write(self.style.SUCCESS(f"Migrados {migrated} usuarios a 'estudiantes' y eliminados grupos legacy."))
