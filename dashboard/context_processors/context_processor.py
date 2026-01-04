# app_name/context_processors.py
import re

def safe_id(text: str) -> str:
    if not text:
        return "menu"
    return re.sub(r'[^a-zA-Z0-9_-]', '', (text or '').replace(" ", "_").lower())

def obtener_menu_contents(request):
    """
    Context processor to generate a menu structure for contents based on user authentication and group membership.
    """
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Opciones de Contenidos',
                'safe_id': safe_id('Opciones de Contenidos'),
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Listar Contenidos', 'safe_id': safe_id('Listar Contenidos'), 'url': '/dashboard/contents/content/ContentListView/'})
            menu[0]['submenus'].append({'nombre': 'Crear Contenido', 'safe_id': safe_id('Crear Contenido'), 'url': '/dashboard/contents/content/ContentCreateView/'})
            menu[0]['submenus'].append({'nombre': 'Listar Categorías', 'safe_id': safe_id('Listar Categorías'), 'url': '/dashboard/contents/categories/CategoryListView/'})
            menu[0]['submenus'].append({'nombre': 'Crear Categoría', 'safe_id': safe_id('Crear Categoría'), 'url': '/dashboard/contents/categories/CategoryCreateView/'})

        return {'menu_contents': menu}
    return {'menu_contents': None}
 
def obtener_menu_dashboard(request):
    """
    Context processor to generate a menu structure for Dashboard based on user authentication and group membership.
    """
    if request.user.is_authenticated:
        menu = [
            {
                'nombre': 'Opciones de Dashboard',
                'safe_id': safe_id('Opciones de Dashboard'),
                'url': '#',
                'submenus': []
            }
        ]
        
        menu[0]['submenus'].append({'nombre': 'Dashboard', 'safe_id': safe_id('Dashboard'), 'url': '/dashboard/'})
        return {'menu_dashboard': menu}
    return {'menu_dashboard': None}
