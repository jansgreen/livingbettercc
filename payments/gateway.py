import os
from dataclasses import dataclass

from .models import PaymentGatewayConfig


@dataclass(frozen=True)
class StripeCredentials:
    mode: str
    secret_key: str
    publishable_key: str
    webhook_secret: str


def get_gateway_config() -> PaymentGatewayConfig:
    return PaymentGatewayConfig.get_solo()


def get_stripe_credentials() -> StripeCredentials:
    config = get_gateway_config()
    mode = config.mode

    if mode == PaymentGatewayConfig.Mode.LIVE:
        secret_key = os.getenv("STRIPE_LIVE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY", "")
        publishable_key = os.getenv("STRIPE_LIVE_PUBLISHABLE_KEY") or os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        webhook_secret = os.getenv("STRIPE_LIVE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET", "")
    else:
        secret_key = os.getenv("STRIPE_TEST_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY", "")
        publishable_key = os.getenv("STRIPE_TEST_PUBLISHABLE_KEY") or os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        webhook_secret = os.getenv("STRIPE_TEST_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET", "")

    return StripeCredentials(
        mode=mode,
        secret_key=secret_key,
        publishable_key=publishable_key,
        webhook_secret=webhook_secret,
    )


def mask_secret(value: str) -> str:
    if not value:
        return "(not configured)"
    if len(value) <= 10:
        return value[:2] + "***"
    return f"{value[:7]}...{value[-4:]}"
