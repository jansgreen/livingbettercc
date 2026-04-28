from django.contrib.auth.models import Group

from .models import SystemFormAssignment


SCHOLARSHIP_STUDENT_INFO_KEY = SystemFormAssignment.SCHOLARSHIP_STUDENT_INFO


def get_system_form_assignment(key: str) -> SystemFormAssignment:
    assignment, _ = SystemFormAssignment.objects.get_or_create(key=key)
    return assignment


def get_group_ids_for_system_form(key: str) -> set[int]:
    assignment = get_system_form_assignment(key)
    return set(assignment.assigned_groups.values_list('id', flat=True))


def group_activates_system_form(group: Group | None, key: str) -> bool:
    if not group:
        return False
    return group.id in get_group_ids_for_system_form(key)

