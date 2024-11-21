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
    return {
        'menu_setting': [
            {
                'nombre': 'Setting', 
                'url': '#',  # Aquí puedes usar # porque no es un enlace directo.
                'submenus': [
                {'nombre': 'Crear Metadata', 'url': '/metadata/create/'}, 
                {'nombre': 'Listar Metadata', 'url': '/metadata/metadata/'},
                {'nombre': 'Carousel', 'url': '/page/carouselPageFunction/'},
                {'nombre': 'Crear Pestaña', 'url': '/page/crear_PageCategory/'},
                {'nombre': 'Listar Pestaña y Posiciones', 'url': '/page/listar_categorias_y_PagePosition/'},
                {'nombre': 'Crear Contenido de la Pestaña', 'url': '/page/create_page_content/'},
                {'nombre': 'Listar Contenido de la Pestaña', 'url': '/page/page-content-list/'},

                ]
            }
        ]
    }
