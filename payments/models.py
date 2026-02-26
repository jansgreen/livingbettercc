from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator

User = get_user_model()


class Payment(models.Model):
	STATUS_INITIATED = "initiated"
	STATUS_PAID = "paid"
	STATUS_FAILED = "failed"
	STATUS_REFUNDED = "refunded"
	STATUS_CANCELLED = "cancelled"
	STATUS_DISPUTED = "disputed"

	PURPOSE_SHOP_ORDER = "shop_order"
	PURPOSE_CLASSROOM_ENROLLMENT = "classroom_enrollment"

	STATUS_CHOICES = [
		(STATUS_INITIATED, "initiated"),
		(STATUS_PAID, "paid"),
		(STATUS_FAILED, "failed"),
		(STATUS_REFUNDED, "refunded"),
		(STATUS_CANCELLED, "cancelled"),
		(STATUS_DISPUTED, "disputed"),
	]

	PURPOSE_CHOICES = [
		(PURPOSE_SHOP_ORDER, "shop_order"),
		(PURPOSE_CLASSROOM_ENROLLMENT, "classroom_enrollment"),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
	amount_cents = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	currency = models.CharField(max_length=10, default="usd")
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INITIATED)
	provider = models.CharField(max_length=20, default="stripe")

	stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
	stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)

	purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
	# Generic reference to the domain object (order_id or enrollment_id)
	reference_id = models.CharField(max_length=64)

	metadata = models.JSONField(default=dict, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=["provider", "status"]),
			models.Index(fields=["purpose", "reference_id"]),
		]

	def __str__(self):
		return f"Payment #{self.id} {self.status} {self.amount_cents}{self.currency}"


class StripeEvent(models.Model):
	event_id = models.CharField(max_length=255, unique=True)
	event_type = models.CharField(max_length=255)
	processed_at = models.DateTimeField(null=True, blank=True)
	payload = models.JSONField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	def mark_processed(self):
		self.processed_at = timezone.now()
		self.save(update_fields=["processed_at"])

	def __str__(self):
		return f"StripeEvent {self.event_type} ({self.event_id})"


class Receipt(models.Model):
	payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="receipt")
	receipt_number = models.CharField(max_length=20, unique=True)
	issued_at = models.DateTimeField(default=timezone.now)
	billing_email = models.EmailField(null=True, blank=True)

	# Snapshot of payment amounts
	amount_cents = models.PositiveIntegerField()
	currency = models.CharField(max_length=10, default="usd")

	html_snapshot = models.TextField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-issued_at", "-id"]

	def __str__(self):
		return f"Receipt {self.receipt_number}"

	def get_absolute_url(self):
		from django.urls import reverse
		return reverse("payments:receipt_detail", kwargs={"receipt_number": self.receipt_number})

	@staticmethod
	def generate_receipt_number(now=None):
		"""
		Generate unique receipt number in format LB-YYYY-000001.
		"""
		now = now or timezone.now()
		year = now.strftime("%Y")
		prefix = f"LB-{year}-"
		last = (
			Receipt.objects.filter(receipt_number__startswith=prefix)
			.order_by("receipt_number")
			.last()
		)
		if last:
			try:
				seq = int(last.receipt_number.split("-")[-1]) + 1
			except Exception:
				seq = 1
		else:
			seq = 1
		return f"{prefix}{seq:06d}"


class PaymentGatewayConfig(models.Model):
	class Mode(models.TextChoices):
		TEST = "test", "Test"
		LIVE = "live", "Live"

	mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.TEST)
	updated_at = models.DateTimeField(auto_now=True)
	updated_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="payment_gateway_updates",
	)

	class Meta:
		verbose_name = "Payment Gateway Configuration"
		verbose_name_plural = "Payment Gateway Configuration"

	def __str__(self):
		return f"Stripe mode: {self.mode}"

	@classmethod
	def get_solo(cls):
		obj, _ = cls.objects.get_or_create(pk=1, defaults={"mode": cls.Mode.TEST})
		return obj
