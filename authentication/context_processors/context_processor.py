from urllib3 import request
from authentication.models import Profiles
import logging
from django.urls import reverse
from authentication.models import Directives
logger = logging.getLogger(__name__)



def obtener_menu_auth(request):
    from django.urls import NoReverseMatch
    menu_auth = []
    if not request.user.is_authenticated:
        return {'menu_auth': menu_auth}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = request.user.groups.filter(name='tecnico').exists()
    is_facilitador = request.user.groups.filter(name='facilitador').exists()

    menu = {
        'nombre': 'Profile',
        'url': '#',
        'submenus': []
    }

    try:
        # Staff/admin: acceso total
        if is_staff:
            menu['submenus'].append({'nombre': 'Crear Biografia', 'url': reverse('profile_create')})
            menu['submenus'].append({'nombre': 'Lista de Perfil', 'url': reverse('profile_list')})
            menu['submenus'].append({'nombre': 'Crear Profile', 'url': reverse('profile_create')})
            menu['submenus'].append({'nombre': 'Customer Form', 'url': reverse('customer_form')})
            menu['submenus'].append({'nombre': 'Customer List', 'url': reverse('customer_list')})
            menu['submenus'].append({'nombre': 'Crear Directivo', 'url': reverse('directives_create')})
            menu['submenus'].append({'nombre': 'Ver Lista de Estudiantes', 'url': reverse('students:student_list_view')})
            menu['submenus'].append({'nombre': 'Crear Nuevo Estudiante', 'url': reverse('students:student_create_view')})
        elif is_tecnico:
            menu['submenus'].append({'nombre': 'Customer List', 'url': reverse('customer_list')})
        elif is_facilitador:
            menu['submenus'].append({'nombre': 'Crear Profile', 'url': reverse('profile_create')})
        else:
            menu['submenus'].append({'nombre': 'Lista de Perfil', 'url': reverse('profile_list')})
    except NoReverseMatch:
        # Fallback mínimo
        menu['submenus'].append({'nombre': 'Perfil', 'url': '/auth/profile/'})

    menu_auth.append(menu)
    return {'menu_auth': menu_auth}
    

def obtener_formbuilder_menu(request):
    from django.urls import NoReverseMatch
    formbuilder_menu = []
    if not request.user.is_authenticated:
        return {'formbuilder_menu': formbuilder_menu}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = request.user.groups.filter(name='tecnico').exists()
    is_facilitador = request.user.groups.filter(name='facilitador').exists()

    menu = {
        'nombre': 'Form Builder',
        'url': '#',
        'submenus': []
    }

    try:
        # Staff/admin: acceso total
        if is_staff:
            menu['submenus'].append({'nombre': 'Formbuilder', 'url': reverse('formbuilder:form_list')})
            menu['submenus'].append({'nombre': 'Crear Formulario', 'url': reverse('formbuilder:form_create')})
            menu['submenus'].append({'nombre': 'Lista Formularios Completados', 'url': reverse('formbuilder:completed_forms_list')})
            menu['submenus'].append({'nombre': 'Lista de Facilitadores', 'url': reverse('formbuilder:facilitador_list_view')})
            menu['submenus'].append({'nombre': 'Mis Formularios Completados', 'url': reverse('formbuilder:my_user_completed_forms')})
        # Técnico: solo ver completados y facilitadores
        elif is_tecnico:
            menu['submenus'].append({'nombre': 'Lista Formularios Completados', 'url': reverse('formbuilder:completed_forms_list')})
            menu['submenus'].append({'nombre': 'Lista de Facilitadores', 'url': reverse('formbuilder:facilitador_list_view')})
        # Facilitador: solo ver y llenar formularios, ver sus completados
        elif is_facilitador:
            menu['submenus'].append({'nombre': 'Formbuilder', 'url': reverse('formbuilder:form_list')})
            menu['submenus'].append({'nombre': 'Mis Formularios Completados', 'url': reverse('formbuilder:my_user_completed_forms')})
        # Otros usuarios autenticados: solo ver sus completados
        else:
            menu['submenus'].append({'nombre': 'Mis Formularios Completados', 'url': reverse('formbuilder:my_user_completed_forms')})
    except NoReverseMatch:
        # Fallback: menú mínimo si reverse falla
        menu['submenus'].append({'nombre': 'Formbuilder', 'url': '/auth/formbuilder/'})

    formbuilder_menu.append(menu)
    logger.warning(f"[CTX] obtener_formbuilder_menu => {type(formbuilder_menu)} | {formbuilder_menu}")
    return {'formbuilder_menu': formbuilder_menu}


# authentication/context_processors/context_processor.py


def obtener_menu_directives(request):
    from django.urls import NoReverseMatch
    menu_directives = []
    if not request.user.is_authenticated:
        return {'menu_directives': menu_directives}

    is_directiva = request.user.groups.filter(name="Directiva").exists()
    is_admin = request.user.is_superuser

    if not is_directiva and not is_admin:
        return {'menu_directives': menu_directives}

    menu = {
        'nombre': 'Directiva',
        'url': '#',
        'submenus': []
    }

    try:
        menu['submenus'].append({'nombre': 'Ver Directiva', 'url': reverse('directives_list')})
        if is_admin:
            menu['submenus'].append({'nombre': 'Crear Nuevo Directivo', 'url': reverse('directives_create')})
        try:
            directive = Directives.objects.get(user=request.user)
            menu['submenus'].append({'nombre': 'Ver Mi Perfil Público', 'url': reverse('directives_detail', args=[directive.pk])})
            menu['submenus'].append({'nombre': 'Editar Mi Perfil', 'url': reverse('directives_update', args=[directive.pk])})
        except Directives.DoesNotExist:
            menu['submenus'].append({'nombre': 'Completar Mi Perfil de Directivo', 'url': reverse('directives_create')})
    except NoReverseMatch:
        menu['submenus'].append({'nombre': 'Directiva', 'url': '/auth/directives/'})

    menu_directives.append(menu)
    return {'menu_directives': menu_directives}
