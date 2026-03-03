from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User

from authentication.groups.models import Invitation


CANONICAL_GROUPS = {
    "coordinadores": ["coordinador", "coordinadores"],
    "tecnicos": ["tecnico", "tecnicos"],
    "Facilitadores": ["facilitador", "facilitadores", "Facilitadores"],
    "estudiantes": ["student", "students", "estudiante", "estudiantes", "Student", "Students", "Estudiante", "Estudiantes"],
    "estudiantes_becados": ["student_becados", "students_becados", "estudiante_becado", "estudiantes_becados"],
    "directivas": ["directiva", "directivas", "Directiva", "Directivas", "directives", "Directives"],
    "customers": ["customer", "customers", "custumer", "custumers"],
}


class Command(BaseCommand):
    help = "Normalize group names to canonical plural groups and assign default 'customers' to users without groups."

    def handle(self, *args, **options):
        # Ensure canonical groups exist
        canonical_objs = {}
        for canonical in CANONICAL_GROUPS.keys():
            group, _ = Group.objects.get_or_create(name=canonical)
            canonical_objs[canonical] = group

        # Map alias name -> canonical group object
        alias_to_canonical = {}
        for canonical, aliases in CANONICAL_GROUPS.items():
            for alias in aliases:
                alias_to_canonical[alias.lower()] = canonical_objs[canonical]

        # Reassign users from alias groups to canonical groups
        migrated = 0
        for user in User.objects.all().prefetch_related("groups"):
            user_group_names = [g.name for g in user.groups.all()]
            for name in user_group_names:
                canonical = alias_to_canonical.get(name.lower())
                if canonical and canonical not in user.groups.all():
                    user.groups.add(canonical)
                    migrated += 1
            # Remove alias groups (non-canonical) from user
            for g in list(user.groups.all()):
                if g.name.lower() in alias_to_canonical and g.name not in CANONICAL_GROUPS:
                    user.groups.remove(g)

        # Update invitations to canonical groups
        for invitation in Invitation.objects.select_related("group"):
            canonical = alias_to_canonical.get(invitation.group.name.lower())
            if canonical and invitation.group != canonical:
                invitation.group = canonical
                invitation.save(update_fields=["group"])

        # Delete alias groups
        for alias, canonical in alias_to_canonical.items():
            if alias not in CANONICAL_GROUPS:
                Group.objects.filter(name__iexact=alias).exclude(id=canonical.id).delete()

        # Assign default group to users without any group
        default_group = canonical_objs["customers"]
        defaulted = 0
        for user in User.objects.all().prefetch_related("groups"):
            if user.groups.count() == 0:
                user.groups.add(default_group)
                defaulted += 1

        self.stdout.write(self.style.SUCCESS(f"Groups normalized. Migrated memberships: {migrated}. Defaulted users: {defaulted}."))
