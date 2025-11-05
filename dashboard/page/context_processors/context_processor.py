from ..models import Footer, PageSection

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
            menu[0]['submenus'].append({'nombre': 'Crear Página', 'url': '/dashboard/page/create/'})
            menu[0]['submenus'].append({'nombre': 'Listar Páginas', 'url': '/dashboard/page/'})
            menu[0]['submenus'].append({'nombre': 'Crear Sección', 'url': '/dashboard/page/sections/create/'})
            menu[0]['submenus'].append({'nombre': 'Listar Secciones', 'url': '/dashboard/page/sections/sections_list/'})


            


        return {'menu_setting': menu}
    return {'menu_setting': None}  # Retornar None si no tiene acceso

def obtener_navbar(request):
    """
    Context processor to add page sections to the context.
    """
    try:
        sections = PageSection.objects.all()
    except PageSection.DoesNotExist:
        sections = None
    return {'menu_home': sections}