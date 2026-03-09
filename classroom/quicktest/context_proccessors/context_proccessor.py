from django.urls import reverse
from django.utils.text import slugify

from classroom.quicktest.models import QuickTestDefinition


def obtener_menu_quicktest(request):
    # Flat, staff-only menu for managing QuickTests
    if not request.user.is_authenticated:
        return {"menu_quicktest": []}

    user = request.user
    if not (user.is_staff or user.is_superuser):
        return {"menu_quicktest": []}

    submenus = [
        {"nombre": "Panel Tests", "url": reverse("quicktest:quicktest_list")},
        {"nombre": "Listar QuickTests", "url": reverse("quicktest:qdef_list")},
        {"nombre": "Crear QuickTest", "url": reverse("quicktest:qdef_create")},
    ]

    menu_quicktest = [
        {
            "nombre": "Examenes y Firmas",
            "safe_id": "quicktests",
            "submenus": submenus,
        }
    ]

    return {"menu_quicktest": menu_quicktest}
