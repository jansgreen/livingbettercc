from urllib3 import request
from authentication.models import Profiles
import logging
from django.urls import reverse
from authentication.models import Directives
logger = logging.getLogger(__name__)


def obtener_menu_auth(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Profile',
                'url': '#',
                'submenus': []
            }
        ]

        # Dynamically generate the URL for "Mi Perfil"
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Crear Biografia', 'url': '/auth/profile/edit_biography/'})

        if request.user.is_authenticated and request.user.has_perm('auth.can_create_posts'):
            menu[0]['submenus'].append({'nombre': 'Lista de Perfil', 'url': '/auth/profile/list/'})
            menu[0]['submenus'].append({'nombre': 'Crear Profile', 'url': '/auth/profile/create/'})
            menu[0]['submenus'].append({'nombre': 'Customer Form', 'url': '/auth/customer_form/'})
            menu[0]['submenus'].append({'nombre': 'Customer List', 'url': '/auth/customers/'})
            menu[0]['submenus'].append({'nombre': 'Crear Directivo', 'url': '/auth/directives/DirectivesCreate/'})
            menu[0]['submenus'].append({'nombre': 'Ver Lista de Estudiantes', 'url': '/auth/students/student_list_view/'})
            menu[0]['submenus'].append({'nombre': 'Crear Nuevo Estudiate', 'url': '/auth/students/student_create_view/'})
        return {'menu_auth': []}
    else:
        return {'menu_auth': []}
    
def obtener_formbuilder_menu(request):
    formbuilder_menu = []
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        formbuilder_menu = [
            {
                'nombre': 'Form Builder',
                'url': '#',
                'submenus': []
            }
        ]

        from django.urls import NoReverseMatch
        try:
            if user_has_module_access:
                formbuilder_menu[0]['submenus'].append({'nombre': 'Formbuilder', 'url': reverse('formbuilder:form_list')})
                formbuilder_menu[0]['submenus'].append({'nombre': 'Lista Formularios Completados', 'url': reverse('formbuilder:completed_forms_list')})
                formbuilder_menu[0]['submenus'].append({'nombre': 'Crear Formulario', 'url': reverse('formbuilder:form_create')} )
            # Common links available to authenticated users
            formbuilder_menu[0]['submenus'].append({'nombre': 'Mis Formularios Completados', 'url': reverse('formbuilder:my_user_completed_forms')})
            formbuilder_menu[0]['submenus'].append({'nombre': 'Lista de Facilitadores', 'url': reverse('formbuilder:facilitador_list_view')})
            formbuilder_menu[0]['submenus'].append({'nombre': 'Mis Formularios Completados (Usuario)', 'url': reverse('formbuilder:my_user_completed_forms')})
        except NoReverseMatch:
            # If any of the named routes are missing, fall back to the hardcoded paths
            formbuilder_menu[0]['submenus'].append({'nombre': 'Formbuilder', 'url': '/auth/formbuilder/'})
            formbuilder_menu[0]['submenus'].append({'nombre': 'Lista Formularios Completados', 'url': '/auth/formbuilder/completed/completed_forms/'})
            formbuilder_menu[0]['submenus'].append({'nombre': 'Crear Formulario', 'url': '/auth/formbuilder/create/'} )
            formbuilder_menu[0]['submenus'].append({'nombre': 'Mis Formularios Completados', 'url': '/auth/formbuilder/completed/completed_forms/'})
            formbuilder_menu[0]['submenus'].append({'nombre': 'Lista de Facilitadores', 'url': '/auth/formbuilder/facilitador/facilitador_list_view/'})
            formbuilder_menu[0]['submenus'].append({'nombre': 'Mis Formularios Completados (Usuario)', 'url': '/auth/formbuilder/facilitador_list_view/'})
    logger.warning(f"[CTX] obtener_formbuilder_menu => {type(formbuilder_menu)} | {formbuilder_menu}")
    return {'formbuilder_menu': formbuilder_menu}


# authentication/context_processors/context_processor.py

def obtener_menu_directives(request):
    """
    Muestra opciones de Directiva según el rol:
    
    - Admin / Superuser → Puede ver lista, crear, editar cualquier miembro.
    - Directivo normal → Solo puede ver lista y editar su propio perfil.
    """

    menu_directives = []  # Siempre lista, nunca None.

    if not request.user.is_authenticated:
        return {'menu_directives': menu_directives}

    is_directiva = request.user.groups.filter(name="Directiva").exists()
    is_admin = request.user.is_superuser

    # Si no es directivo y no es administrador → no mostrar menú.
    if not is_directiva and not is_admin:
        return {'menu_directives': menu_directives}

    # Base del menú
    menu_directives = [
        {
            'nombre': 'Directiva',
            'url': '#',
            'submenus': [
                {'nombre': 'Ver Directiva', 'url': reverse('directives_list')},
            ]
        }
    ]

    # Si es administrador → puede crear nuevos miembros
    if is_admin:
        menu_directives[0]['submenus'].append(
            {'nombre': 'Crear Nuevo Directivo', 'url': reverse('directives_create')}
        )

    # Intentamos obtener el perfil de la directiva actual
    try:
        directive = Directives.objects.get(user=request.user)

        # Ver biografía pública
        menu_directives[0]['submenus'].append({
            'nombre': 'Ver Mi Perfil Público',
            'url': reverse('directives_detail', args=[directive.pk])
        })

        # Editar sus datos (biografía, foto, cargo, redes)
        menu_directives[0]['submenus'].append({
            'nombre': 'Editar Mi Perfil',
            'url': reverse('directives_update', args=[directive.pk])
        })

    except Directives.DoesNotExist:
        # Si aún no tiene perfil pero pertenece a directiva → crear su archivo
        menu_directives[0]['submenus'].append({
            'nombre': 'Completar Mi Perfil de Directivo',
            'url': reverse('directives_create')
        })

    return {'menu_directives': menu_directives}
