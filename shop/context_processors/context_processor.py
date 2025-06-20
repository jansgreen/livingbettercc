def obtener_menu_shop(request):
    menu = [
        {
            'nombre': 'Tienda',
            'url': '#',
            'submenus': []
        }
    ]
    
    menu[0]['submenus'].append({'nombre': 'Shop', 'url': '/shop/ '})
    
    # Check if the user has module access
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        if user_has_module_access:
            # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
            if request.user.has_perm('shop.can_create_shop'):
                menu[0]['submenus'].append({'nombre': 'Crear Producto', 'url': '/shop/create/'})
            
            if request.user.has_perm('shop.can_view_category'):
                menu[0]['submenus'].append({'nombre': 'Categoria', 'url': '/shop/categories/'})
    
    return {'menu_shop': menu}

