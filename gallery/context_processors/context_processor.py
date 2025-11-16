def obtener_gallery_img(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [{
            'nombre': 'Opciones de Gallery',
            'url': '#',
            'submenus': []
        }]
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Galeria', 'url': '/gallery/'})
            menu[0]['submenus'].append({'nombre': 'Subir Imagen', 'url': '/gallery/create/'})

        return {'menu_gallery':menu}
    return {'menu_gallery':[]}