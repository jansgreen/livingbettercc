from ..models import Footer

def footer_context(request):
    """
    Añade el contenido del footer al contexto global
    """
    footer = Footer.objects.last()  # Obtener el último registro de Footer
    return {
        'footer': footer
    }


def obtener_menu_setting(request):
        if request.user.is_authenticated:
            user_in_manager_group = (request.user.is_authenticated and request.user.groups.filter(name='admin').exists() or request.user.groups.filter(name='Superusuario').exists() )
            menu = [
                {
                    'nombre': 'Setting',
                    'url': '#',
                    'submenus': []
                }
            ]
            
            if user_in_manager_group:
                menu[0]['submenus'].append({'nombre': 'Crear Metadata', 'url': '/metadata/create/'})
                menu[0]['submenus'].append({'nombre': 'Listar Metadata', 'url': '/metadata/metadata/'})
                menu[0]['submenus'].append({'nombre': 'Carousel', 'url': '/page/carouselPageFunction/'})
                menu[0]['submenus'].append({'nombre': 'Crear Pestaña', 'url': '/page/crear_PageCategory/'})
                menu[0]['submenus'].append({'nombre': 'Crear Contenido de la Pestaña', 'url': '/page/create_page_content/'})
                menu[0]['submenus'].append({'nombre': 'Listar Contenido de la Pestaña', 'url': '/page/page-content-list/'})

            return {'menu_setting': menu}
        else:
            menu = None
            return {'menu_setting': menu}