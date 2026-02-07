# your_project/context_processors.py
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from core.menu_builder import build_menu, safe_id


def bootstrap_css(request):
    return {'BOOTSTRAP_CSS': settings.BOOTSTRAP_CSS}

def bootstrap_js(request):
    return {'BOOTSTRAP_JS': settings.BOOTSTRAP_JS}

def obtener_menu_report_activity(request):
    if not request.user.is_authenticated:
        return {'menu_report_activity': []}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = request.user.groups.filter(name='tecnico').exists()
    is_facilitador = request.user.groups.filter(name='facilitador').exists()

    def _safe_url(name, fallback_url, **kwargs):
        try:
            return reverse(name, kwargs=kwargs)
        except NoReverseMatch:
            return fallback_url
        except Exception:
            return fallback_url

    submenus = []

    # Staff/admin: acceso total
    if is_staff:
        submenus.extend([
            {'nombre': 'Nueva Categoría', 'url': _safe_url('report_categories_create', '/report_categories/new/')},
            {'nombre': 'Lista de Categorías', 'url': _safe_url('report_categories_list', '/report_categories/')},
            {'nombre': 'Nuevo Reporte', 'url': _safe_url('report_create', '/reportes/nuevo/')},
            {'nombre': 'Lista de Reportes', 'url': _safe_url('report_list', '/reportes/lista/')},
            {'nombre': 'Detalle de Reporte', 'url': _safe_url('report_detail', '/reportes/detalle/', pk=1)},  # pk=1 como ejemplo
            {'nombre': 'Editar Reporte', 'url': _safe_url('report_update', '/reportes/editar/', pk=1)},
            {'nombre': 'Eliminar Reporte', 'url': _safe_url('report_delete', '/reportes/eliminar/', pk=1)},

        ])
    # Técnico: solo ver lista y detalle
    elif is_tecnico:
        submenus.extend([
            {'nombre': 'Lista de Reportes', 'url': _safe_url('report_list', '/reportes/lista/')},
            {'nombre': 'Detalle de Reporte', 'url': _safe_url('report_detail', '/reportes/detalle/', pk=1)},
        ])
    # Facilitador: solo crear y ver lista
    elif is_facilitador:
        submenus.extend([
            {'nombre': 'Nuevo Reporte', 'url': _safe_url('report_create', '/reportes/nuevo/')},
            {'nombre': 'Lista de Reportes', 'url': _safe_url('report_list', '/reportes/lista/')},
        ])
    # Otros usuarios autenticados


    menu = build_menu(request.user, 'Reportes', submenus, url='#')
    return {'menu_report_activity': [menu] if menu else []}
