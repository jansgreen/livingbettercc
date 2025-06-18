# app_name/context_processors.py

from dashboard.models import CategoriaMenu, MenuItem

def navbar_menu(request):
    categorias = CategoriaMenu.objects.prefetch_related('menus').all()
    return {'navbar_categorias': categorias}


def navbar_menuitems(request):
    """
    Context processor to add menu items to the context.
    """
    categorias = CategoriaMenu.objects.prefetch_related('menus').all()
    menuitems = MenuItem.objects.all()
    return {'navbar_menuitems': menuitems}
