from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("control-center/", views.control_center, name="control_center"),
    path("control-center/switch-mode/", views.switch_mode, name="switch_mode"),
    path("control-center/toggle-course-payment/", views.toggle_course_payment_required, name="toggle_course_payment_required"),
    path("control-center/grant-course-access/", views.grant_course_access, name="grant_course_access"),
    path("transactions/", views.payments_list, name="payments_list"),
    path("receipts/", views.receipts_list, name="receipts_list"),
    path("reports/", views.reports_view, name="reports"),
    path("disputes/", views.disputes_view, name="disputes"),
    path("start/enrollment/<int:enrollment_id>/", views.start_checkout_for_enrollment, name="start_enrollment_checkout"),
    path("start/order/<int:order_id>/", views.start_checkout_for_order, name="start_order_checkout"),
    path("receipt/<str:receipt_number>/", views.receipt_detail, name="receipt_detail"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
]
