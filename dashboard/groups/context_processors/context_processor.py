from django.urls import reverse
from core.menu_builder import build_menu

def obtener_menu_groups(request):
    submenus = []
    if request.user.is_authenticated:
        # Gate all group actions behind 'groups.access_module'
        submenus.append({'nombre': 'Lista de Usuarios', 'url': reverse('user_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Lista de Grupos', 'url': reverse('group_list'), 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Invitar Amigo', 'url': reverse('invite_friend'), 'perm': 'groups.access_module'})

    menu = build_menu(request.user, 'Grupo', submenus, url='#')
    return {'menu_groups': [menu] if menu else []}