def obtener_menu_groups(request):
    return {
        'menu_groups': [
            {
            'nombre': 'Groups', 
            'url': '#',
            'submenus': [
                {'nombre': 'Listar Usuarios', 'url': '/groups/user_list/'},
                {'nombre': 'Ver Grupos', 'url': '/groups/'}, 
                {'nombre': 'Invitar', 'url': '/groups/invite/'}, 
            ]
            }
        ]
    }