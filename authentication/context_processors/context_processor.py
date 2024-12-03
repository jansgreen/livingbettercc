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
            
            if user_in_manager_group:
                menu[0]['submenus'].append({'nombre': 'Crear Biografia', 'url': '/auth/edit_biography/'})

            if request.user.is_authenticated and request.user.has_perm('auth.can_create_posts'):
                menu[0]['submenus'].append({'nombre': 'Perfil', 'url': '/auth/ProfileFunction/'})
                menu[0]['submenus'].append({'nombre': 'Editar Perfil', 'url': '/auth/edit_profile/'})
            return {'menu_auth': menu}
        else:
            menu = None
            return {'menu_auth': menu}