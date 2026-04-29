import logging

from django.urls import NoReverseMatch, reverse

from authentication.address.models import Address
from authentication.models import Directives, Profiles
from authentication.models.profiles import ScholarshipStudentInfo
from core.group_utils import has_group
from core.menu_builder import build_menu, safe_id
from formbuilder.system_forms import (
    SCHOLARSHIP_STUDENT_INFO_KEY,
    get_group_ids_for_system_form,
)

logger = logging.getLogger(__name__)


def obtener_menu_auth(request):
    if not request.user.is_authenticated:
        return {'menu_auth': []}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = has_group(request.user, "tecnicos")
    is_facilitador = has_group(request.user, "facilitadores")

    submenus = []
    try:
        profile = Profiles.objects.filter(user=request.user).first()
        residential_address = Address.objects.filter(user=request.user, address_type="residencial").first()
        address_is_complete = bool(
            residential_address
            and residential_address.street
            and residential_address.city
            and residential_address.state
        )
        scholarship_info = ScholarshipStudentInfo.objects.filter(user=request.user).first()
        scholarship_group_ids = get_group_ids_for_system_form(SCHOLARSHIP_STUDENT_INFO_KEY)
        user_group_ids = set(request.user.groups.values_list("id", flat=True))
        needs_or_has_scholarship_info = bool(
            scholarship_info
            or scholarship_group_ids.intersection(user_group_ids)
        )

        submenus.append({'nombre': 'Mi Perfil', 'url': reverse('authentication:profile_detail')})
        if profile:
            submenus.append({'nombre': 'Editar Mi Perfil', 'url': reverse('authentication:profile_update', args=[profile.pk])})
        else:
            submenus.append({'nombre': 'Completar Mi Perfil', 'url': reverse('authentication:profile_create')})

        if address_is_complete and residential_address:
            submenus.append({'nombre': 'Editar Direccion', 'url': reverse('authentication:address:address_update', args=[residential_address.pk])})
        else:
            submenus.append({
                'nombre': 'Completar Direccion',
                'url': reverse('authentication:address:address_create', kwargs={'address_type': 'residencial', 'pk': request.user.id}),
            })

        if needs_or_has_scholarship_info:
            label = 'Editar Datos Becado' if scholarship_info and scholarship_info.is_complete() else 'Completar Datos Becado'
            submenus.append({'nombre': label, 'url': reverse('complete_scholarship_info')})

        if is_staff:
            submenus.append({'nombre': 'Lista de Perfil', 'url': reverse('authentication:profile_list')})
            submenus.append({'nombre': 'Customer List', 'url': reverse('authentication:customer_list')})
            submenus.append({'nombre': 'Ver Lista de Estudiantes', 'url': reverse('authentication:students:student_list_view')})
            submenus.append({'nombre': 'Crear Nuevo Estudiante', 'url': reverse('authentication:students:student_create')})
        elif is_tecnico:
            submenus.append({'nombre': 'Customer List', 'url': reverse('authentication:customer_list')})
        elif is_facilitador:
            pass
    except NoReverseMatch:
        submenus.append({'nombre': 'Perfil', 'url': '/auth/profile/'})

    menu = build_menu(request.user, 'Mi Cuenta', submenus, url='#')
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
        if is_admin:
            submenus.append({'nombre': 'Lista de Directivos', 'url': reverse('authentication:directives_list')})
            submenus.append({'nombre': 'Crear Nuevo Directivo', 'url': reverse('authentication:directives_create')})

        directive = Directives.objects.filter(user=request.user).first()
        if directive:
            submenus.append({'nombre': 'Ver Mi Perfil Publico', 'url': reverse('view_bio', args=[directive.pk])})
            submenus.append({'nombre': 'Editar Mi Biografia', 'url': reverse('authentication:directives_update', args=[directive.pk])})
        else:
            submenus.append({'nombre': 'Crear Mi Biografia', 'url': reverse('authentication:directives_create')})
    except NoReverseMatch:
        submenus.append({'nombre': 'Directiva', 'url': '/auth/directives/'})

    menu = build_menu(request.user, 'Directiva', submenus, url='#')
    return {'menu_directives': [menu] if menu else []}


def obtener_menu_messages(request):
    if not request.user.is_authenticated:
        return {'menu_messages': []}

    if not (request.user.is_staff or request.user.is_superuser):
        return {'menu_messages': []}

    submenus = []
    try:
        submenus.append({'nombre': 'Enviar mensaje', 'url': reverse('authentication:send_certified_message')})
    except NoReverseMatch:
        submenus.append({'nombre': 'Enviar mensaje', 'url': '/auth/messages/certified/'})

    menu = build_menu(request.user, 'Mensajes', submenus, url='#')
    return {'menu_messages': [menu] if menu else []}


def safe_id(text: str) -> str:
    from core.menu_builder import safe_id as _safe
    return _safe(text)


def obtener_menu_groups(request):
    submenus = []
    if request.user.is_authenticated:
        submenus.append({'nombre': 'Lista de Usuarios', 'url': reverse('user_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Lista de Grupos', 'url': reverse('group_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Invitar Amigo', 'url': reverse('invite_friend'), 'perm': 'groups.access_module'})

    menu = build_menu(request.user, 'Grupo', submenus, url='#')
    return {'menu_groups': [menu] if menu else []}
