from django.contrib.auth.models import Group
from django.db.models import Q


ROLE_ALIASES = {
    "tecnicos": {"tecnicos", "tecnico", "técnico"},
    "facilitadores": {"facilitadores", "facilitador"},
    "estudiantes": {"estudiantes", "estudiante"},
    "estudiantes_becados": {"estudiantes_becados", "estudiante_becado"},
    "directivas": {"directivas", "directiva"},
}

CANONICAL_GROUP_NAME = {
    "tecnicos": "tecnicos",
    "facilitadores": "Facilitadores",
    "estudiantes": "estudiantes",
    "estudiantes_becados": "estudiantes_becados",
    "directivas": "directivas",
}


def group_names(user) -> set[str]:
    if not user or not getattr(user, "is_authenticated", False):
        return set()
    return {name.strip().lower() for name in user.groups.values_list("name", flat=True)}


def resolve_aliases(aliases_or_role) -> set[str]:
    if isinstance(aliases_or_role, str):
        key = aliases_or_role.strip().lower()
        if key in ROLE_ALIASES:
            return set(ROLE_ALIASES[key])
        return {key}
    return {str(x).strip().lower() for x in aliases_or_role if str(x).strip()}


def has_group(user, aliases_or_role) -> bool:
    names = group_names(user)
    aliases = resolve_aliases(aliases_or_role)
    return bool(names & aliases)


def ensure_group(canonical_name: str) -> Group:
    group, _ = Group.objects.get_or_create(name=canonical_name)
    return group


def canonical_group_for(aliases_or_role: str) -> str:
    key = aliases_or_role.strip().lower()
    return CANONICAL_GROUP_NAME.get(key, aliases_or_role)


def group_q(aliases_or_role) -> Q:
    aliases = resolve_aliases(aliases_or_role)
    query = Q()
    for alias in aliases:
        query |= Q(groups__name__iexact=alias)
    return query

