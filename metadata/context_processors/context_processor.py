from metadata.models import MetaData

def metadata_context(request):
    metadata_homepage = MetaData.objects.filter(category='homepage').first()
    return {
        'meta_title': metadata_homepage.title if metadata_homepage else 'Título por defecto',
        'meta_description': metadata_homepage.description if metadata_homepage else 'Descripción por defecto',
        'meta_keywords': metadata_homepage.keywords if metadata_homepage else 'palabras, clave, por, defecto',
        'meta_search_image': metadata_homepage.search_image.url if metadata_homepage and metadata_homepage.search_image else '',
        'meta_icon': metadata_homepage.icon.url if metadata_homepage and metadata_homepage.icon else '',
        'page_type': 'homepage' if request.path == '/' else 'blog' if 'blog' in request.path else 'other',
    }

def obtener_menu_metadata(request):
        if request.user.is_authenticated:
            user_in_manager_metadata = (request.user.is_authenticated and request.user.groups.filter(name='Superusuario').exists() )
            menu = [
                {
                    'nombre': 'Metas',
                    'url': '#',
                    'submenus': []
                }
            ]
            
            if user_in_manager_metadata:
                menu[0]['submenus'].append({'nombre': 'Crear Metadata', 'url': '/metadata/create/'})
                menu[0]['submenus'].append({'nombre': 'Listar Metadata', 'url': '/metadata/metadata/'})

            return {'menu_metadata': menu}
        else:
            menu = None
            return {'menu_metadata': menu}