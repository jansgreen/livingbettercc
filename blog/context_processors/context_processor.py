from ..models import blogCategory
# authentication/context_processors.py

Category = blogCategory.objects.exists()
def obtener_menu_blog(request):
    if Category:
        menu = [
            {
                'nombre': 'Blog',
                'url': '#',
                'submenus': []
            }
        ]
        
        menu[0]['submenus'].append({'nombre': 'Ver', 'url': '/blog/'})

        # Agregar "Crear Post" para usuarios con el permiso "can_create_posts"
        if request.user.is_authenticated and request.user.has_perm('blog.can_create_posts'):
            menu[0]['submenus'].append({'nombre': 'Crear Post', 'url': '/blog/post_create/'})
        
        return {'menu_blog': menu}
    else:
        menu = None
        return {'menu_blog': menu}


