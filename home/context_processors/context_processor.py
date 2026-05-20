# your_project/context_processors.py
from django.conf import settings
from django.urls import reverse, NoReverseMatch
from core.group_utils import has_group
from core.menu_builder import build_menu, safe_id


def bootstrap_css(request):
    return {'BOOTSTRAP_CSS': settings.BOOTSTRAP_CSS}

def bootstrap_js(request):
    return {'BOOTSTRAP_JS': settings.BOOTSTRAP_JS}

def obtener_menu_report_activity(request):
    if not request.user.is_authenticated:
        return {'menu_report_activity': []}

    is_staff = request.user.is_staff or request.user.is_superuser
    is_tecnico = has_group(request.user, "tecnicos")
    is_facilitador = has_group(request.user, "facilitadores")

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
            {'nombre': 'Nuevo Reporte Online', 'url': _safe_url('certifications:online_report_create', '/online-report/new/')},
            {'nombre': 'Reportes Online', 'url': _safe_url('certifications:online_report_list', '/online-report/')},
        ])
    # Técnico: solo ver lista y detalle


    menu = build_menu(request.user, 'Reportes', submenus, url='#')
    return {'menu_report_activity': [menu] if menu else []}
