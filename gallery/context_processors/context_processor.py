from core.menu_builder import build_menu

def obtener_gallery_img(request):
    submenus = []
    if request.user.is_authenticated:
        # Gate via 'groups.access_module'
        submenus.append({'nombre': 'Galeria', 'url': '/gallery/', 'perm': 'groups.access_module'})
        submenus.append({'nombre': 'Subir Imagen', 'url': '/gallery/create/', 'perm': 'groups.access_module'})

    menu = build_menu(request.user, 'Opciones de Gallery', submenus, url='#')
    return {'menu_gallery': [menu] if menu else []}