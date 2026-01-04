from core.menu_builder import build_menu, safe_id

def obtener_menu_contents(request):
    """Build Contents menu filtered by permissions."""
    submenus = []
    if request.user.is_authenticated:
        # Require module access for content actions
        submenus.append({'nombre': 'Listar Contenidos', 'url': '/dashboard/contents/content/ContentListView/', 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Crear Contenido', 'url': '/dashboard/contents/content/ContentCreateView/', 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Listar Categorías', 'url': '/dashboard/contents/categories/CategoryListView/', 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Crear Categoría', 'url': '/dashboard/contents/categories/CategoryCreateView/', 'perm': 'groups.access_module'})

    menu = build_menu(request.user, 'Opciones de Contenidos', submenus, url='#')
    return {'menu_contents': [menu] if menu else []}
 
def obtener_menu_dashboard(request):
    """Build Dashboard menu; visible to authenticated users."""
    submenus = []
    if request.user.is_authenticated:
        submenus.append({'nombre': 'Dashboard', 'url': '/dashboard/'})

    menu = build_menu(request.user, 'Opciones de Dashboard', submenus, url='#')
    return {'menu_dashboard': [menu] if menu else []}
