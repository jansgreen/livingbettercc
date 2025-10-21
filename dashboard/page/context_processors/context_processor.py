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
            menu[0]['submenus'].append({'nombre': 'Crear Metadata', 'url': '/dashboard/metadata/create/'})
            menu[0]['submenus'].append({'nombre': 'Listar Metadata', 'url': '/dashboard/metadata/metadata/'})
            menu[0]['submenus'].append({'nombre': 'Carousel', 'url': '/dashboard/page/carouselPageFunction/'})
            menu[0]['submenus'].append({'nombre': 'Crear Pestaña', 'url': '/dashboard/page/crear_PageCategory/'})
            menu[0]['submenus'].append({'nombre': 'Listar Pestañas', 'url': '/dashboard/page/listar_categorias_y_PagePosition/'})
            menu[0]['submenus'].append({'nombre': 'Crear Contenido de la Pestaña', 'url': '/dashboard/page/create_page_content/'})
            menu[0]['submenus'].append({'nombre': 'Listar Contenido de la Pestaña', 'url': '/dashboard/page/page_content_list/'})


        return {'menu_setting': menu}
    return {'menu_setting': None}  # Retornar None si no tiene acceso