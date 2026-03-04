import logging

from django.urls import NoReverseMatch, reverse

from core.group_utils import has_group
from core.menu_builder import build_menu

logger = logging.getLogger(__name__)


def _safe_url(name: str, fallback: str = "#", *args, **kwargs) -> str:
    try:
        return reverse(name, *args, **kwargs)
    except NoReverseMatch:
        return fallback


def obtener_formbuilder_menu(request):
    if not request.user.is_authenticated:
        return {"formbuilder_menu": []}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = has_group(request.user, "tecnicos")
    is_facilitador = has_group(request.user, "facilitadores")
    submenus = []

    if is_staff:
        submenus.extend(
            [
                {"nombre": "Panel del Formularios", "url": _safe_url("formbuilder:form_list", "/formbuilder/")},
                {
                    "nombre": "Panel de Facilitadores",
                    "url": _safe_url("formbuilder:facilitador_list_view", "/formbuilder/facilitadores/"),
                },
                {
                    "nombre": "Panel delTecnico",
                    "url": _safe_url("formbuilder:panel_tecnico", "/formbuilder/tecnico/panel/"),
                },
                {
                    "nombre": "Mis Formularios Completados",
                    "url": _safe_url("formbuilder:my_user_completed_forms", "/formbuilder/my-completed/"),
                },
                {"nombre": "Invitar Estudiante Becado", "url": f"{_safe_url('invite_friend', '#')}?group=estudiantes_becados"},
                {"nombre": "Invitar Facilitador", "url": f"{_safe_url('invite_friend', '#')}?group=Facilitadores"},
                {"nombre": "Invitar Tecnico", "url": f"{_safe_url('invite_friend', '#')}?group=tecnicos"},
                {"nombre": "Invitar Coordinador", "url": f"{_safe_url('invite_friend', '#')}?group=coordinadores"},
            ]
        )
    elif is_tecnico:
        submenus.extend(
            [
                {"nombre": "Lista Formularios Completados", "url": _safe_url("formbuilder:completed_forms_list", "/formbuilder/completed/")},
                {
                    "nombre": "Lista de Facilitadores",
                    "url": _safe_url("formbuilder:facilitador_list_view", "/formbuilder/facilitadores/"),
                },
                {
                    "nombre": "Panel del Tecnico",
                    "url": _safe_url("formbuilder:panel_tecnico", "/formbuilder/tecnico/panel/"),
                },
            ]
        )
    elif is_facilitador:
        submenus.extend(
            [
                {
                    "nombre": "Mis Formularios Completados",
                    "url": _safe_url("formbuilder:my_user_completed_forms", "/formbuilder/my-completed/"),
                },
            ]
        )
    else:
        submenus.extend(
            [
                {
                    "nombre": "Mis Formularios Completados",
                    "url": _safe_url("formbuilder:my_user_completed_forms", "/formbuilder/my-completed/"),
                },
            ]
        )

    menu = build_menu(request.user, "Gestiones y Formularios", submenus, url="#")
    logger.warning(f"[CTX] obtener_formbuilder_menu => {type(menu)} | {menu}")
    return {"formbuilder_menu": [menu] if menu else []}

