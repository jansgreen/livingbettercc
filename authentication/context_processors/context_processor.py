def obtener_menu_auth(request):
    # Verificar si el usuario pertenece al grupo 'manager'
    user_in_manager_group = (
        request.user.is_authenticated and 
        request.user.groups.filter(name='manager').exists()
    )

    # Construir submenús condicionalmente
    submenus = [
        {'nombre': 'Ver', 'url': '/auth/ProfileFunction/'},

    ]

    if user_in_manager_group:
        submenus.append({'nombre': 'Crear Biografia', 'url': '/auth/edit_biography/'})


    # Retornar el menú
    return {
        'menu_auth': [
            {
                'nombre': 'Profile',
                'url': '#',  # Aquí puedes usar # porque no es un enlace directo.
                'submenus': submenus,
            }
        ]
    }
