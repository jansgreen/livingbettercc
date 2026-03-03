from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Merge legacy student groups into 'estudiantes' group, reassign users, and delete old groups."

    def handle(self, *args, **options):
        legacy_names = ["students", "student", "estudiante", "Student", "Students", "Estudiante"]
        old_groups = list(Group.objects.filter(name__in=legacy_names))
        new_group, _ = Group.objects.get_or_create(name="estudiantes")

        if not old_groups:
            self.stdout.write(self.style.NOTICE("No existen grupos legacy de estudiantes. Ninguna accion necesaria."))
            return

        migrated = 0
        for old_group in old_groups:
            users = list(old_group.user_set.all())
            for user in users:
                new_group.user_set.add(user)
                migrated += 1
                self.stdout.write(f"Movido usuario: {user.username}")
            old_group.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Migrados {migrated} usuarios a 'estudiantes' y eliminados grupos legacy.")
        )
