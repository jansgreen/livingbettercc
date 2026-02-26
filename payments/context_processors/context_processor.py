from django.urls import reverse

from core.menu_builder import build_menu


def obtener_menu_payments(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return {"menu_payments": []}

    submenus = [
        {"nombre": "Control Stripe", "url": reverse("payments:control_center")},
        {"nombre": "Transacciones", "url": reverse("payments:payments_list")},
        {"nombre": "Facturas", "url": reverse("payments:receipts_list")},
        {"nombre": "Informes", "url": reverse("payments:reports")},
        {"nombre": "Reclamos", "url": reverse("payments:disputes")},
    ]
    menu = build_menu(request.user, "Pagos", submenus, url="#")
    return {"menu_payments": [menu] if menu else []}
