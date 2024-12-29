from ..cart import Cart

def obtener_menu_cart(request):
    cart = Cart(request)
    cart_length = len(cart)
    print(cart_length)
    menu_cart = '/cart/'
    return {
        'cart_length': cart_length,
        'menu_cart': menu_cart
    }

def obtener_menu_shop(request):
    menu = [
        {
            'nombre': 'Tienda',
            'url': '#',
            'submenus': []
        }
    ]
    
    menu[0]['submenus'].append({'nombre': 'Shop', 'url': '/shop/ '})
    
    # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
    if request.user.is_authenticated and request.user.has_perm('shop.can_create_shop'):
        menu[0]['submenus'].append({'nombre': 'Crear Producto', 'url': '/shop/create/'})
    
    if request.user.is_authenticated and request.user.has_perm('shop.can_view_category'):
        menu[0]['submenus'].append({'nombre': 'Categoria', 'url': '/shop/categories/'}) 
    return {'menu_shop': menu}