from django.urls import reverse

def obtener_menu_groups(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Grupo',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Lista de Usuarios', 'url': reverse('user_list')})
            menu[0]['submenus'].append({'nombre': 'Lista de Grupos', 'url': reverse('group_list')})
            menu[0]['submenus'].append({'nombre': 'Invitar Amigo', 'url': reverse('invite_friend')})
        
        return {'menu_groups': menu}
    else:
        return {'menu_groups': None}