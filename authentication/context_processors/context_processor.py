from urllib3 import request
from authentication.models import Profiles
from dashboard.views import menu

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
        profile_id = Profiles.objects.filter(user=request.user).values_list('id', flat=True).first()
        print("Profile ID:", profile_id)
        if profile_id:
            menu[0]['submenus'].append({'nombre': 'Mi Perfil', 'url': f'/auth/profile/'})

            if user_has_module_access:
                menu[0]['submenus'].append({'nombre': 'Crear Biografia', 'url': '/auth/profile/edit_biography/'})

            if request.user.is_authenticated and request.user.has_perm('auth.can_create_posts'):
                menu[0]['submenus'].append({'nombre': 'Lista de Perfil', 'url': '/auth/profile/list/'})
        menu[0]['submenus'].append({'nombre': 'Crear Profile', 'url': '/auth/profile/create/'})

        # Add new submenu items
        menu[0]['submenus'].extend([
            {'nombre': 'Customer Form', 'url': '/auth/customer_form/'},
            {'nombre': 'Customer List', 'url': '/auth/customers/'},
            {'nombre': 'Create Customer', 'url': '/auth/customers/create/'},
            {'nombre': 'Crear Directivo', 'url': '/auth/directives/DirectivesCreate/'},
        ])
        
        return {'menu_auth': menu}
    else:
        menu = None
        return {'menu_auth': menu}
    
def obtener_formbuilder_menu(request):
    formbuilder_menu = None
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        formbuilder_menu = [
            {
                'nombre': 'Form Builder',
                'url': '#',
                'submenus': []
            }
        ]

        if user_has_module_access:
            formbuilder_menu[0]['submenus'].append({'nombre': 'Formbuilder', 'url': '/auth/formbuilder/'})
    return {'formbuilder_menu': formbuilder_menu}
