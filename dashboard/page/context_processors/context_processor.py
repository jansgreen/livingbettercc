from ..models import Footer

def footer_context(request):
    """
    Añade el contenido del footer al contexto global
    """
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        if user_has_module_access:
            footer = Footer.objects.last()  # Obtener el último registro de Footer
            return {
                'footer': footer
            }
    return {'footer': None}  # Retornar None si no tiene acceso


def obtener_menu_setting(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Setting',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Crear Metadata', 'url': '/metadata/create/'})
            menu[0]['submenus'].append({'nombre': 'Listar Metadata', 'url': '/metadata/metadata/'})
            menu[0]['submenus'].append({'nombre': 'Carousel', 'url': '/page/carouselPageFunction/'})
            menu[0]['submenus'].append({'nombre': 'Crear Pestaña', 'url': '/page/crear_PageCategory/'})
            menu[0]['submenus'].append({'nombre': 'Crear Contenido de la Pestaña', 'url': '/page/create_page_content/'})
            menu[0]['submenus'].append({'nombre': 'Listar Contenido de la Pestaña', 'url': '/page/page-content-list/'})

        return {'menu_setting': menu}
    return {'menu_setting': None}  # Retornar None si no tiene acceso