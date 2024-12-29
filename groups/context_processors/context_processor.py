from django.urls import reverse

def obtener_menu_groups(request):
    if request.user.is_authenticated:
        user_in_manager_group = request.user.groups.filter(name='Superusuario').exists()
        menu = [
            {
                'nombre': 'Grupo',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_in_manager_group:
            menu[0]['submenus'].append({'nombre': 'Lista de Usuarios', 'url': reverse('user_list')})
            menu[0]['submenus'].append({'nombre': 'Lista de Grupos', 'url': reverse('group_list')})
            menu[0]['submenus'].append({'nombre': 'Crear Grupo', 'url': reverse('group_create')})
            menu[0]['submenus'].append({'nombre': 'Invitar Amigo', 'url': reverse('invite_friend')})
        
        return {'menu_groups': menu}
    else:
        return {'menu_groups': None}