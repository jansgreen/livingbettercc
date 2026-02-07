from django.urls import reverse
from ..cart import Cart
import logging
logger = logging.getLogger(__name__)

def obtener_menu_cart(request):
    cart = Cart(request)  # Instancia de la clase Cart

    # Calcula la cantidad total de productos en el carrito
    cart_length = sum(cart.cart.values())

    # Define la URL para ver el carrito
    menu_cart = reverse('shop:checkout:checkout_list')
    logger.warning(f"[CTX] obtener_menu_cart => {type(menu_cart)} | {menu_cart}")

    return {
        'cart_length': cart_length,
        'menu_cart': menu_cart
    }
