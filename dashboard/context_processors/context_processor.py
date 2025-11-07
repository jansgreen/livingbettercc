# app_name/context_processors.py

def obtener_menu_contents(request):
    """
    Context processor to generate a menu structure for contents based on user authentication and group membership.
    """
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Opciones de Contenidos',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Listar Contenidos', 'url': '/dashboard/contents/content/ContentListView/'})
            menu[0]['submenus'].append({'nombre': 'Crear Contenido', 'url': '/dashboard/contents/content/ContentCreateView/'})
            menu[0]['submenus'].append({'nombre': 'Listar Categorías', 'url': '/dashboard/contents/categories/CategoryListView/'})
            menu[0]['submenus'].append({'nombre': 'Crear Categoría', 'url': '/dashboard/contents/categories/CategoryCreateView/'})

        return {'menu_contents': menu}
    return {'menu_contents': None}

