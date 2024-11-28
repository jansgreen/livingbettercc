from shop.models import Cart, CartItem

def obtener_menu_cart(request):
    # Iniciar cantidad en 0
    cantidad = 0

    # Verificar si el usuario tiene un carrito activo
    if request.user.is_authenticated:
        cart = Cart.objects.filter(id=request.session.get('cart_id')).first()
        if cart:
            cantidad = CartItem.objects.filter(cart=cart).count()

    # Construir submenús condicionalmente
    submenus = [
        {'nombre': 'Cart', 'url': '/shop/cart/'},
    ]

    # Retornar el menú con la cantidad
    return {
        'menu_cart': [
            {
                'nombre': 'Cart',
                'url': '#',  # Aquí puedes usar # porque no es un enlace directo.
                'submenus': submenus,
                'cantidad': cantidad,  # Incluye la cantidad en el contexto
            }
        ]
    }


def obtener_menu_shop(request):
    menu = [
        {
            'nombre': 'Tienda',
            'url': '#',
            'submenus': []
        }
    ]
    
    # Agregar "Lista de Post" para usuarios con el permiso "can_view_posts"
    if request.user.is_authenticated and request.user.has_perm('shop.can_view_posts'):
        menu[0]['submenus'].append({'nombre': 'Shop', 'url': '/shop/ '})
    
    # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
    if request.user.is_authenticated and request.user.has_perm('shop.can_create_shop'):
        menu[0]['submenus'].append({'nombre': 'Crear Producto', 'url': '/shop/create/'})
    
    if request.user.is_authenticated and request.user.has_perm('shop.can_view_cart'):
        menu[0]['submenus'].append({'nombre': 'ver Carrito', 'url': '/shop/cart/'}) 

    if request.user.is_authenticated and request.user.has_perm('shop.can_view_category'):
        menu[0]['submenus'].append({'nombre': 'Categoria', 'url': '/shop/categories/'}) 
    return {'menu_shop': menu}