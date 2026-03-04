from authentication.models import Profiles
import logging
from django.urls import reverse
from authentication.models import Directives
from core.group_utils import has_group
from core.menu_builder import build_menu, safe_id
from django.urls import NoReverseMatch

logger = logging.getLogger(__name__)

def obtener_menu_auth(request):
    from django.urls import NoReverseMatch
    if not request.user.is_authenticated:
        return {'menu_auth': []}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = has_group(request.user, "tecnicos")
    is_facilitador = has_group(request.user, "facilitadores")

    submenus = []
    try:
        if is_staff:
            submenus.append({'nombre': 'Crear Biografia', 'url': reverse('profile_create')})
            submenus.append({'nombre': 'Lista de Perfil', 'url': reverse('profile_list')})
            submenus.append({'nombre': 'Crear Profile', 'url': reverse('profile_create')})
            submenus.append({'nombre': 'Customer Form', 'url': reverse('customer_form')})
            submenus.append({'nombre': 'Customer List', 'url': reverse('customer_list')})
            submenus.append({'nombre': 'Crear Directivo', 'url': reverse('directives_create')})
            submenus.append({'nombre': 'Ver Lista de Estudiantes', 'url': reverse('students:student_list_view')})
            submenus.append({'nombre': 'Crear Nuevo Estudiante', 'url': reverse('students:student_create_view')})
        elif is_tecnico:
            submenus.append({'nombre': 'Customer List', 'url': reverse('customer_list')})
        elif is_facilitador:
            submenus.append({'nombre': 'Crear Profile', 'url': reverse('profile_create')})
        else:
            submenus.append({'nombre': 'Lista de Perfil', 'url': reverse('profile_list')})
    except NoReverseMatch:
        submenus.append({'nombre': 'Perfil', 'url': '/auth/profile/'})

    menu = build_menu(request.user, 'Profile', submenus, url='#')
    return {'menu_auth': [menu] if menu else []}

def obtener_menu_directives(request):
    if not request.user.is_authenticated:
        return {'menu_directives': []}

    is_directiva = has_group(request.user, "directivas")
    is_admin = request.user.is_superuser

    if not is_directiva and not is_admin:
        return {'menu_directives': []}

    submenus = []

    try:
        submenus.append({'nombre': 'Ver Directiva', 'url': reverse('directives_list')})
        if is_admin:
            submenus.append({'nombre': 'Crear Nuevo Directivo', 'url': reverse('directives_create')})
        try:
            directive = Directives.objects.get(user=request.user)
            submenus.append({'nombre': 'Ver Mi Perfil Público', 'url': reverse('directives_detail', args=[directive.pk])})
            submenus.append({'nombre': 'Editar Mi Perfil', 'url': reverse('directives_update', args=[directive.pk])})
        except Directives.DoesNotExist:
            submenus.append({'nombre': 'Completar Mi Perfil de Directivo', 'url': reverse('directives_create')})
    except NoReverseMatch:
        submenus.append({'nombre': 'Directiva', 'url': '/auth/directives/'})

    menu = build_menu(request.user, 'Directiva', submenus, url='#')
    return {'menu_directives': [menu] if menu else []}

def safe_id(text: str) -> str:
    # Deprecated: use core.menu_builder.safe_id instead (kept for backward compat if imported elsewhere)
    from core.menu_builder import safe_id as _safe
    return _safe(text)


def obtener_menu_groups(request):
    submenus = []
    if request.user.is_authenticated:
        # Gate all group actions behind 'groups.access_module'
        submenus.append({'nombre': 'Lista de Usuarios', 'url': reverse('user_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Lista de Grupos', 'url': reverse('group_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Invitar Amigo', 'url': reverse('invite_friend'), 'perm': 'groups.access_module'})

    menu = build_menu(request.user, 'Grupo', submenus, url='#')
    return {'menu_groups': [menu] if menu else []}
