# authentication/context_processors.py

def obtener_menu_blog(request):
    return {
        'menu_blog': [
            {
                'nombre': 'Blog', 
                'url': '#',  # Aquí puedes usar # porque no es un enlace directo.
                'submenus': [
                    {'nombre': 'Lista de Post', 'url': '/blog/'},
                    {'nombre': 'Crear Post', 'url': '/blog/post_create/'},
                ]
            }
        ]
    }
