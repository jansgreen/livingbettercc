from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("start/enrollment/<int:enrollment_id>/", views.start_checkout_for_enrollment, name="start_enrollment_checkout"),
    path("start/order/<int:order_id>/", views.start_checkout_for_order, name="start_order_checkout"),
    path("receipt/<str:receipt_number>/", views.receipt_detail, name="receipt_detail"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
]
