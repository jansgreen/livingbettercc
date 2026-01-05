
import logging
from django.urls import reverse, NoReverseMatch
from core.menu_builder import build_menu, safe_id
logger = logging.getLogger(__name__)

def _safe_url(name: str, fallback: str = '#', *args, **kwargs) -> str:
    try:
        return reverse(name, *args, **kwargs)
    except NoReverseMatch:
        return fallback

def obtener_formbuilder_menu(request):
    if not request.user.is_authenticated:
        return {'formbuilder_menu': []}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = request.user.groups.filter(name='tecnico').exists()
    is_facilitador = request.user.groups.filter(name='facilitador').exists()

    submenus = []

    # Staff/admin: acceso total
    if is_staff:
        submenus.extend([
            {'nombre': 'Formbuilder', 'url': _safe_url('formbuilder:form_list', '/formbuilder/')},
            {'nombre': 'Crear Formulario', 'url': _safe_url('formbuilder:form_create', '/formbuilder/create/')},
            {'nombre': 'Lista Formularios Completados', 'url': _safe_url('formbuilder:completed_forms_list', '/formbuilder/completed/')},
            {'nombre': 'Lista de Facilitadores', 'url': _safe_url('formbuilder:facilitador_list_view', '/formbuilder/facilitadores/')},
            {'nombre': 'Mis Formularios Completados', 'url': _safe_url('formbuilder:my_user_completed_forms', '/formbuilder/my-completed/')},
            {'nombre': 'Inscribir Facilitador', 'url': _safe_url('formbuilder:enroll_facilitador', '/formbuilder/enroll_facilitador/')},
            {'nombre': 'Invitar Facilitador', 'url': f"{_safe_url('invite_friend', '#')}?group=facilitador"},
        ])
    # Técnico: solo ver completados y facilitadores
    elif is_tecnico:
        submenus.extend([
            {'nombre': 'Lista Formularios Completados', 'url': _safe_url('formbuilder:completed_forms_list', '/formbuilder/completed/')},
            {'nombre': 'Lista de Facilitadores', 'url': _safe_url('formbuilder:facilitador_list_view', '/formbuilder/facilitadores/')},
        ])
    # Facilitador: ver/llenar formularios y ver sus completados
    elif is_facilitador:
        submenus.extend([
            {'nombre': 'Formbuilder', 'url': _safe_url('formbuilder:form_list', '/formbuilder/')},
            {'nombre': 'Mis Formularios Completados', 'url': _safe_url('formbuilder:my_user_completed_forms', '/formbuilder/my-completed/')},
        ])
    # Otros usuarios autenticados
    else:
        submenus.append({'nombre': 'Mis Formularios Completados', 'url': _safe_url('formbuilder:my_user_completed_forms', '/formbuilder/my-completed/')})

    menu = build_menu(request.user, 'Form Builder', submenus, url='#')
    logger.warning(f"[CTX] obtener_formbuilder_menu => {type(menu)} | {menu}")
    return {'formbuilder_menu': [menu] if menu else []}