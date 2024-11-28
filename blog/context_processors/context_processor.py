# authentication/context_processors.py


def obtener_menu_blog(request):
    menu = [
        {
            'nombre': 'Blog',
            'url': '#',
            'submenus': []
        }
    ]
    
    # Agregar "Lista de Post" para usuarios con el permiso "can_view_posts"
    if request.user.is_authenticated and request.user.has_perm('blog.can_view_posts'):
        menu[0]['submenus'].append({'nombre': 'Lista de Post', 'url': '/blog/'})
    
    # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
    if request.user.is_authenticated and request.user.has_perm('blog.can_create_posts'):
        menu[0]['submenus'].append({'nombre': 'Crear Post', 'url': '/blog/post_create/'})
    
    return {'menu_blog': menu}

