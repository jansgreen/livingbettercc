from metadata.models import MetaData

def metadata_context(request):
    metadata_homepage = MetaData.objects.filter(category='homepage').first()
    metadata_blog = MetaData.objects.filter(category='blog').first()

    return {
        'meta_title': metadata_homepage.title if metadata_homepage else 'Título por defecto',
        'meta_description': metadata_homepage.description if metadata_homepage else 'Descripción por defecto',
        'meta_keywords': metadata_homepage.keywords if metadata_homepage else 'palabras, clave, por, defecto',
        'meta_search_image': metadata_homepage.search_image.url if metadata_homepage and metadata_homepage.search_image else '',
        'meta_icon': metadata_homepage.icon.url if metadata_homepage and metadata_homepage.icon else '',
        
        'meta_blog_title': metadata_blog.title if metadata_blog else 'Título del Blog por defecto',
        'meta_blog_description': metadata_blog.description if metadata_blog else 'Descripción del Blog por defecto',
        'meta_blog_keywords': metadata_blog.keywords if metadata_blog else 'palabras, clave, blog, por, defecto',
        'meta_blog_search_image': metadata_blog.search_image.url if metadata_blog and metadata_blog.search_image else '',
        
        'page_type': 'homepage' if request.path == '/' else 'blog' if 'blog' in request.path else 'other',
    }

def obtener_menu_metadata(request):
    return {
        'menu_metadata': [
            {
            'nombre': 'Metadata', 
            'url': '#',
            'submenus': [
                {'nombre': 'Crear Metadata', 'url': '/metadata/create/'}, 
                {'nombre': 'Listar Metadata', 'url': '/metadata/metadata/'}, 

            ]
            }
        ]
    }