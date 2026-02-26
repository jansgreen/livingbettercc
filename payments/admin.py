from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Payment, Receipt, StripeEvent, PaymentGatewayConfig


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = (
		"user",
		"amount",
		"status",
		"purpose",
		"reference_id",
		"receipt_column",
		"created_at",
	)
	list_filter = ("status", "purpose", "provider")
	search_fields = ("id", "user__username", "reference_id", "stripe_session_id")
	readonly_fields = ("receipt_link",)
	actions = ["open_receipt"]

	def amount(self, obj: Payment):
		return f"{obj.amount_cents/100:.2f} {obj.currency.upper()}"
	amount.short_description = "amount"

	def receipt_column(self, obj: Payment):
		if hasattr(obj, "receipt") and obj.receipt:
			url = reverse("admin:payments_receipt_change", args=[obj.receipt.id])
			return mark_safe(f'<a href="{url}">{obj.receipt.receipt_number}</a>')
		return "—"
	receipt_column.short_description = "receipt"

	def receipt_link(self, obj: Payment):
		if hasattr(obj, "receipt") and obj.receipt:
			url = reverse("admin:payments_receipt_change", args=[obj.receipt.id])
			return mark_safe(f'Receipt: <a href="{url}">{obj.receipt.receipt_number}</a>')
		return "No receipt"

	def open_receipt(self, request, queryset):
		links = []
		for p in queryset:
			if hasattr(p, 'receipt') and p.receipt:
				url = reverse("admin:payments_receipt_change", args=[p.receipt.id])
				links.append(f"{p.id}: {url}")
		if links:
			self.message_user(request, mark_safe("<br>".join(links)))
		else:
			self.message_user(request, "No receipts found for selected payments.")
	open_receipt.short_description = "Open receipt links"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
	list_display = ("receipt_number", "payment", "user", "issued_at", "amount")
	list_filter = ("issued_at", "payment__status", "payment__purpose")
	search_fields = ("receipt_number", "payment__id", "payment__user__username", "billing_email")

	def user(self, obj: Receipt):
		return obj.payment.user

	def amount(self, obj: Receipt):
		return f"{obj.amount_cents/100:.2f} {obj.currency.upper()}"


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
	list_display = ("event_id", "event_type", "processed_at", "created_at")
	search_fields = ("event_id", "event_type")
	readonly_fields = ("event_id", "event_type", "processed_at", "payload", "created_at")


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
	list_display = ("mode", "updated_at", "updated_by")
	readonly_fields = ("updated_at",)

	def has_add_permission(self, request):
		# Singleton config
		return not PaymentGatewayConfig.objects.exists()
