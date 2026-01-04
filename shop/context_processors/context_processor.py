import re

def safe_id(text: str) -> str:
    if not text:
        return "menu"
    return re.sub(r'[^a-zA-Z0-9_-]', '', (text or '').replace(" ", "_").lower())

def obtener_menu_shop(request):
    menu = [
        {
            'nombre': 'Tienda',
            'safe_id': safe_id('Tienda'),
            'url': '#',
            'submenus': []
        }
    ]
    
    # Make "Shop" visible to all users
    menu[0]['submenus'].append({'nombre': 'Shop', 'safe_id': safe_id('Shop'), 'url': '/shop/product_list/'})
    
    # Check if the user has module access
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        if user_has_module_access:
            # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
            if request.user.has_perm('shop.can_create_shop'):
                menu[0]['submenus'].append({'nombre': 'Crear Producto', 'safe_id': safe_id('Crear Producto'), 'url': '/shop/create/'})
            
            if request.user.has_perm('shop.can_view_category'):
                menu[0]['submenus'].append({'nombre': 'Categoria', 'safe_id': safe_id('Categoria'), 'url': '/shop/categories/'})
    
    return {'menu_shop': menu}

