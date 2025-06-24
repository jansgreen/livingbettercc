from authentication.models import Profiles

def obtener_menu_auth(request):
    if request.user.is_authenticated:
        user_in_manager_group = (request.user.is_authenticated and request.user.groups.filter(name='manager').exists())
        menu = [
            {
                'nombre': 'Profile',
                'url': '#',
                'submenus': []
            }
        ]

        # Dynamically generate the URL for "Mi Perfil"
        profile_id = Profiles.objects.filter(user=request.user).values_list('id', flat=True).first()
        if profile_id:
            menu[0]['submenus'].append({'nombre': 'Mi Perfil', 'url': f'/auth/profile/{profile_id}/'})

            if user_in_manager_group:
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