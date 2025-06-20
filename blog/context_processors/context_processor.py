from ..models import blogCategory
# authentication/context_processors.py

Category = blogCategory.objects.exists()

def obtener_menu_blog(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Blog',
                'url': '#',
                'submenus': []
            }
        ]
        
        menu[0]['submenus'].append({'nombre': 'Ver', 'url': '/blog/'})

        # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
        if request.user.has_perm('blog.can_create_posts'):
            menu[0]['submenus'].append({'nombre': 'Crear Post', 'url': '/blog/post_create/'})

        # Agregar las URLs adicionales al menú
        menu[0]['submenus'].append({'nombre': 'Lista de Posts', 'url': '/blog/post_list'})
        menu[0]['submenus'].append({'nombre': 'Categorías', 'url': '/blog/CategoryListView/'})
        menu[0]['submenus'].append({'nombre': 'Nueva Categoría', 'url': '/blog/categories/new/'})
       
        return {'menu_blog': menu}
    else:
        menu = None
        return {'menu_blog': menu}
    return {'menu_blog': None}


