from metadata.models import MetaData

def metadata_context(request):
    # Filtrar los metadatos por categoría
    metadata_homepage = MetaData.objects.filter(category='homepage').first()
    metadata_blog = MetaData.objects.filter(category='blog').first()

    return {
        'meta_title': metadata_homepage.title if metadata_homepage else 'Título por defecto',
        'meta_description': metadata_homepage.description if metadata_homepage else 'Descripción por defecto',
        'meta_keywords': metadata_homepage.keywords if metadata_homepage else 'palabras, clave, por, defecto',
        'meta_blog_title': metadata_blog.title if metadata_blog else 'Título del Blog por defecto',
        'meta_blog_description': metadata_blog.description if metadata_blog else 'Descripción del Blog por defecto',
        'meta_blog_keywords': metadata_blog.keywords if metadata_blog else 'palabras, clave, blog, por, defecto',
    }


def obtener_menus(request):
    menus = [
        {
            'nombre': 'metadata', 
            'url': '#',
            'submenus': [
                {'nombre': 'Listar Usuarios', 'url': '/metadata/create/'},
            ]
        },
    ]
    return {'menus': menus}