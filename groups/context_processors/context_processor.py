def obtener_menu_groups(request):
        if request.user.is_authenticated:
            user_in_manager_group = (request.user.is_authenticated and request.user.groups.filter(name='Superusuario').exists() )
            menu = [
                {
                    'nombre': 'Grupo',
                    'url': '#',
                    'submenus': []
                }
            ]
            
            if user_in_manager_group:
                menu[0]['submenus'].append({'nombre': 'Crear Biografia', 'url': '/auth/edit_biography/'})
                menu[0]['submenus'].append({'nombre': 'Perfil', 'url': '/auth/ProfileFunction/'})
                menu[0]['submenus'].append({'nombre': 'Editar Perfil', 'url': '/auth/edit_profile/'})
            return {'menu_groups': menu}
        else:
            menu = None
            return {'menu_groups': menu}