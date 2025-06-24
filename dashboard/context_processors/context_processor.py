# app_name/context_processors.py

from dashboard.models import CategoriaMenu, MenuItem

def navbar_menu(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        if user_has_module_access:
            categorias = CategoriaMenu.objects.prefetch_related('menus').all()
            return {'navbar_categorias': categorias}
    return {'navbar_categorias': None}
def navbar_menuitems(request):
    """
    Context processor to add menu items to the context.
    """
    try:
        menuitems = MenuItem.objects.all()
    except MenuItem.DoesNotExist:
        menuitems = None
    return {'navbar_menuitems': menuitems}

def obtener_create_menu(request):
    """
    Context processor to generate a menu structure for settings based on user authentication and group membership.
    """
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Opciones de Menus',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Menus', 'url': '/menus'})
            menu[0]['submenus'].append({'nombre': 'Listar Categorías', 'url': '/categorias/'})
            menu[0]['submenus'].append({'nombre': 'Crear Categoría', 'url': '/categorias/create/'})
            menu[0]['submenus'].append({'nombre': 'Actualizar Categoría', 'url': '/categorias/<int:pk>/update/'})
            menu[0]['submenus'].append({'nombre': 'Eliminar Categoría', 'url': '/categorias/<int:pk>/delete/'})
            menu[0]['submenus'].append({'nombre': 'Listar Items del Menú', 'url': '/menuitems/'})
            menu[0]['submenus'].append({'nombre': 'Crear Item del Menú', 'url': '/menuitems/create/'})
            menu[0]['submenus'].append({'nombre': 'Actualizar Item del Menú', 'url': '/menuitems/<int:pk>/update/'})
            menu[0]['submenus'].append({'nombre': 'Eliminar Item del Menú', 'url': '/menuitems/<int:pk>/delete/'})
        
        return {'create_menu': menu}
    return {'create_menu': None}

def obtener_dashboard_menu(request):
    """
    Context processor to generate a menu structure for the dashboard based on user authentication and group membership.
    """
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Dashboard',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Dashboard', 'url': 'dashboard/dashboards/'})
        
        return {'dashboard_menu': menu}
    return {'dashboard_menu': None}