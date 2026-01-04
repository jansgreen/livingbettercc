from django.urls import reverse
import re

def safe_id(text: str) -> str:
    if not text:
        return "menu"
    return re.sub(r'[^a-zA-Z0-9_-]', '', (text or '').replace(" ", "_").lower())

def obtener_menu_groups(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Grupo',
                'safe_id': safe_id('Grupo'),
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Lista de Usuarios', 'safe_id': safe_id('Lista de Usuarios'), 'url': reverse('user_list')})
            menu[0]['submenus'].append({'nombre': 'Lista de Grupos', 'safe_id': safe_id('Lista de Grupos'), 'url': reverse('group_list')})
            menu[0]['submenus'].append({'nombre': 'Invitar Amigo', 'safe_id': safe_id('Invitar Amigo'), 'url': reverse('invite_friend')})
        
        return {'menu_groups': menu}
    else:
        return {'menu_groups': None}