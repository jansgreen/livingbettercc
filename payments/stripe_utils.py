import os
import stripe
from django.urls import reverse

from .models import Payment


stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def _build_success_cancel_urls(request):
    success_env = os.getenv("STRIPE_SUCCESS_URL")
    cancel_env = os.getenv("STRIPE_CANCEL_URL")
    if success_env and cancel_env:
        return success_env, cancel_env
    # Fallback: send to shop landing pages that can link to order detail via session
    try:
        success_url = request.build_absolute_uri(reverse("order_return"))
        cancel_url = request.build_absolute_uri(reverse("order_cancel"))
    except Exception:
        base = request.build_absolute_uri('/')
        success_url = base
        cancel_url = base
    return success_url, cancel_url


def create_checkout_session(payment: Payment, request):
    """
    Create a Stripe Checkout session for the given Payment.
    Requires metadata fields: payment_id, user_id, purpose, reference_id.
    """
    # Basic line item description based on purpose
    name = "Payment"
    if payment.purpose == Payment.PURPOSE_CLASSROOM_ENROLLMENT:
        name = f"Course Enrollment #{payment.reference_id}"
    elif payment.purpose == Payment.PURPOSE_SHOP_ORDER:
        name = f"Order #{payment.reference_id}"

    success_url, cancel_url = _build_success_cancel_urls(request)

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": payment.currency,
                    "product_data": {"name": name},
                    "unit_amount": payment.amount_cents,
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "payment_id": str(payment.id),
            "user_id": str(payment.user_id),
            "purpose": payment.purpose,
            "reference_id": payment.reference_id,
        },
    )
    return session.id, session.url
