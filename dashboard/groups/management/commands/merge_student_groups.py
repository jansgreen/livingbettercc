from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Merge 'students' group into 'student' group, reassign users, and delete old group." 

    def handle(self, *args, **options):
        old_group = Group.objects.filter(name='students').first()
        new_group, _ = Group.objects.get_or_create(name='student')

        if not old_group:
            self.stdout.write(self.style.NOTICE("No existe el grupo 'students'. Ninguna acción necesaria."))
            return

        users = list(old_group.user_set.all())
        if not users:
            # no users, safe to delete
            old_group.delete()
            self.stdout.write(self.style.SUCCESS("Grupo 'students' eliminado (estaba vacío)."))
            return

        migrated = 0
        for u in users:
            # Add to new group (idempotente)
            new_group.user_set.add(u)
            migrated += 1
            self.stdout.write(f"Movido usuario: {u.username}")

        # After reassigning users, delete the old group
        old_group.delete()
        self.stdout.write(self.style.SUCCESS(f"Migrados {migrated} usuarios de 'students' a 'student' y eliminado 'students'."))
