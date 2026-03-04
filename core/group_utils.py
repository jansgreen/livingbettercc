import re
import unicodedata

from django.contrib.auth.models import Group
from django.db.models import Q


ROLE_ALIASES = {
    "tecnicos": {"tecnicos", "tecnico"},
    "facilitadores": {"facilitadores", "facilitador"},
    "estudiantes": {"estudiantes", "estudiante"},
    "estudiantes_becados": {"estudiantes_becados", "estudiante_becado", "estudiantes becados", "estudiante becado"},
    "directivas": {"directivas", "directiva"},
}

CANONICAL_GROUP_NAME = {
    "tecnicos": "tecnicos",
    "facilitadores": "Facilitadores",
    "estudiantes": "estudiantes",
    "estudiantes_becados": "estudiantes_becados",
    "directivas": "directivas",
}


def _normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", (value or "").strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def group_names(user) -> set[str]:
    if not user or not getattr(user, "is_authenticated", False):
        return set()
    return {_normalize_name(name) for name in user.groups.values_list("name", flat=True)}


def resolve_aliases(aliases_or_role) -> set[str]:
    if isinstance(aliases_or_role, str):
        key = _normalize_name(aliases_or_role)
        if key in ROLE_ALIASES:
            return {_normalize_name(x) for x in ROLE_ALIASES[key]}
        return {key}
    return {_normalize_name(str(x)) for x in aliases_or_role if str(x).strip()}


def has_group(user, aliases_or_role) -> bool:
    names = group_names(user)
    aliases = resolve_aliases(aliases_or_role)
    return bool(names & aliases)


def ensure_group(canonical_name: str) -> Group:
    group, _ = Group.objects.get_or_create(name=canonical_name)
    return group


def canonical_group_for(aliases_or_role: str) -> str:
    key = _normalize_name(aliases_or_role)
    return CANONICAL_GROUP_NAME.get(key, aliases_or_role)


def group_q(aliases_or_role) -> Q:
    aliases = resolve_aliases(aliases_or_role)
    query = Q()
    for alias in aliases:
        # Match against common variants in DB names.
        alias_underscore = alias.replace(" ", "_")
        alias_nospace = alias.replace(" ", "")
        query |= Q(groups__name__iexact=alias)
        query |= Q(groups__name__iexact=alias_underscore)
        query |= Q(groups__name__iexact=alias_nospace)
    return query

