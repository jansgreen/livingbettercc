from dashboard.metadata.models import MetaData

def metadata_context(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        if user_has_module_access:
            try:
                metadata_homepage = MetaData.objects.filter(category='homepage').first()
            except MetaData.DoesNotExist:
                metadata_homepage = None
            return {
                'meta_title': metadata_homepage.title if metadata_homepage else 'Título por defecto',
                'meta_description': metadata_homepage.description if metadata_homepage else 'Descripción por defecto',
                'meta_keywords': metadata_homepage.keywords if metadata_homepage else 'palabras, clave, por, defecto',
                'meta_search_image': metadata_homepage.search_image.url if metadata_homepage and metadata_homepage.search_image else '',
                'meta_icon': metadata_homepage.icon.url if metadata_homepage and metadata_homepage.icon else '',
                'page_type': 'homepage' if request.path == '/' else 'blog' if 'blog' in request.path else 'other',
            }
    return {
        'meta_title': 'Título por defecto',
        'meta_description': 'Descripción por defecto',
        'meta_keywords': 'palabras, clave, por, defecto',
        'meta_search_image': '',
        'meta_icon': '',
        'page_type': 'other',
    }

