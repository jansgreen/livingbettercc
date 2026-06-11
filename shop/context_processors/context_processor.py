from django.urls import reverse
from core.menu_builder import build_menu, safe_id

def obtener_menu_shop(request):
    submenus = []
    # Public submenu
    submenus.append({'nombre': 'Shop', 'url': reverse('shop:product_list')})

    if request.user.is_authenticated:
        # Use actual perms on submenus so helper can filter
        submenus.append({'nombre': 'Crear Producto', 'url': '/shop/create/', 'perm': 'shop.can_create_shop'})
        submenus.append({'nombre': 'Categoria', 'url': '/shop/categories/', 'perm': 'shop.can_view_category'})
        submenus.append({'nombre': 'Mis Productos', 'url': '/shop/product_ds_list/', 'perm': 'shop.can_view_own_products'})

    menu = build_menu(request.user, 'Tienda', submenus, url='#')
    return {'menu_shop': [menu] if menu else []}

