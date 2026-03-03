import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone

import stripe

from .models import Payment, Receipt, StripeEvent
from .stripe_utils import create_checkout_session
from .gateway import get_gateway_config, get_stripe_credentials, mask_secret

from classroom.enrollments.models import Enrollment
from django.contrib.auth.models import Group


def _decimal_to_cents(amount: Decimal) -> int:
	return int((amount * 100).to_integral_value())


def send_payment_email(user_email: str, subject: str, template_name: str, context: dict):
	# Minimal email sender using Django's send_mail; template_name unused for brevity
	message = context.get("message") or subject
	try:
		send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=True)
	except Exception:
		pass


@login_required
def start_checkout_for_enrollment(request, enrollment_id: int):
	enrollment = get_object_or_404(Enrollment, id=enrollment_id)
	if enrollment.user_id != request.user.id:
		return HttpResponse(status=404)
	if enrollment.status != Enrollment.Status.PENDING_PAYMENT:
		return HttpResponseBadRequest("Enrollment not pending payment")

	amount_cents = _decimal_to_cents(enrollment.course.price)

	payment = Payment.objects.create(
		user=request.user,
		amount_cents=amount_cents,
		currency="usd",
		status=Payment.STATUS_INITIATED,
		provider="stripe",
		purpose=Payment.PURPOSE_CLASSROOM_ENROLLMENT,
		reference_id=str(enrollment.id),
		metadata={"course_id": str(enrollment.course_id)},
	)

	try:
		session_id, session_url = create_checkout_session(payment, request)
	except stripe.error.StripeError:
		messages.error(
			request,
			"No se pudo iniciar el pago con Stripe en este momento. Intenta de nuevo en unos minutos.",
		)
		return redirect("courses:my_course")
	except Exception:
		messages.error(
			request,
			"Ocurrio un error inesperado al conectar con el proveedor de pagos.",
		)
		return redirect("courses:my_course")
	payment.stripe_session_id = session_id
	payment.save(update_fields=["stripe_session_id"]) 

	# Backward-compatibility: also create legacy enrollment Payment record
	try:
		from classroom.enrollments.models import Payment as LegacyPayment
		LegacyPayment.objects.create(
			user=request.user,
			course=enrollment.course,
			enrollment=enrollment,
			amount=enrollment.course.price,
			stripe_session_id=session_id,
			status="created",
		)
	except Exception:
		pass

	return redirect(session_url)


@login_required
def start_checkout_for_order(request, order_id: int):
	# Import lazily to avoid circular deps
	from shop.models import Order

	order = get_object_or_404(Order, id=order_id)
	if order.user_id != request.user.id:
		return HttpResponse(status=404)
	if order.status != Order.Status.PENDING_PAYMENT:
		return HttpResponseBadRequest("Order not pending payment")

	amount_cents = int(order.total_cents)

	payment = Payment.objects.create(
		user=request.user,
		amount_cents=amount_cents,
		currency="usd",
		status=Payment.STATUS_INITIATED,
		provider="stripe",
		purpose=Payment.PURPOSE_SHOP_ORDER,
		reference_id=str(order.id),
		metadata={},
	)

	try:
		session_id, session_url = create_checkout_session(payment, request)
	except stripe.error.StripeError:
		messages.error(
			request,
			"No se pudo iniciar el pago con Stripe en este momento. Intenta de nuevo en unos minutos.",
		)
		return redirect("shop:order_detail", order_id=order.id)
	except Exception:
		messages.error(
			request,
			"Ocurrio un error inesperado al conectar con el proveedor de pagos.",
		)
		return redirect("shop:order_detail", order_id=order.id)
	payment.stripe_session_id = session_id
	payment.save(update_fields=["stripe_session_id"]) 

	return redirect(session_url)


@login_required
def receipt_detail(request, receipt_number: str):
	receipt = get_object_or_404(Receipt, receipt_number=receipt_number)
	if not (request.user.is_staff or request.user.id == receipt.payment.user_id):
		return HttpResponseForbidden()
	ctx = {"receipt": receipt, "payment": receipt.payment}
	return render(request, "payments/receipt_detail.html", ctx)


@staff_member_required
def control_center(request):
	if not request.user.is_superuser:
		return HttpResponse(status=404)

	config = get_gateway_config()
	creds = get_stripe_credentials()
	last_event = StripeEvent.objects.order_by("-created_at").first()
	today = timezone.now().date()
	today_stats = Payment.objects.filter(created_at__date=today).aggregate(
		count=Count("id"),
		total=Sum("amount_cents"),
	)

	ctx = {
		"config": config,
		"creds": creds,
		"masked_secret": mask_secret(creds.secret_key),
		"masked_publishable": mask_secret(creds.publishable_key),
		"masked_webhook": mask_secret(creds.webhook_secret),
		"last_event": last_event,
		"today_count": today_stats.get("count") or 0,
		"today_total": (today_stats.get("total") or 0) / 100,
	}
	return render(request, "payments/control_center.html", ctx)


@staff_member_required
def switch_mode(request):
	if not request.user.is_superuser:
		return HttpResponse(status=404)
	if request.method != "POST":
		return HttpResponseBadRequest("POST required")

	requested_mode = (request.POST.get("mode") or "").strip().lower()
	if requested_mode not in {"test", "live"}:
		return HttpResponseBadRequest("Invalid mode")

	config = get_gateway_config()
	config.mode = requested_mode
	config.updated_by = request.user
	config.save(update_fields=["mode", "updated_by", "updated_at"])

	creds = get_stripe_credentials()
	if not creds.secret_key:
		messages.warning(
			request,
			f"Modo cambiado a {requested_mode.upper()}, pero no hay clave secreta configurada para ese modo.",
		)
	else:
		messages.success(request, f"Stripe ahora esta en modo {requested_mode.upper()}.")
	return redirect("payments:control_center")


@staff_member_required
def payments_list(request):
	if not request.user.is_superuser:
		return HttpResponse(status=404)
	payments = Payment.objects.select_related("user").order_by("-created_at")[:200]
	return render(request, "payments/payments_list.html", {"payments": payments})


@staff_member_required
def receipts_list(request):
	if not request.user.is_superuser:
		return HttpResponse(status=404)
	receipts = Receipt.objects.select_related("payment", "payment__user").order_by("-issued_at")[:200]
	return render(request, "payments/receipts_list.html", {"receipts": receipts})


@staff_member_required
def reports_view(request):
	if not request.user.is_superuser:
		return HttpResponse(status=404)
	agg = Payment.objects.values("status").annotate(count=Count("id"), total=Sum("amount_cents")).order_by("status")
	total_paid = Payment.objects.filter(status=Payment.STATUS_PAID).aggregate(total=Sum("amount_cents")).get("total") or 0
	return render(
		request,
		"payments/reports.html",
		{
			"by_status": agg,
			"total_paid": total_paid / 100,
		},
	)


@staff_member_required
def disputes_view(request):
	if not request.user.is_superuser:
		return HttpResponse(status=404)
	disputed_payments = Payment.objects.select_related("user").filter(status=Payment.STATUS_DISPUTED).order_by("-updated_at")[:200]
	dispute_events = StripeEvent.objects.filter(event_type__icontains="dispute").order_by("-created_at")[:200]
	return render(
		request,
		"payments/disputes.html",
		{
			"disputed_payments": disputed_payments,
			"dispute_events": dispute_events,
		},
	)


@csrf_exempt
def stripe_webhook(request):
	creds = get_stripe_credentials()
	webhook_secret = creds.webhook_secret
	payload = request.body
	sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
	if not webhook_secret or not sig_header:
		return HttpResponseBadRequest("Missing webhook secret or signature")

	try:
		event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=webhook_secret)
	except Exception:
		return HttpResponseBadRequest("Invalid signature")

	# Idempotency
	if StripeEvent.objects.filter(event_id=event.get("id")).exists():
		return HttpResponse(status=200)

	se = StripeEvent.objects.create(event_id=event.get("id"), event_type=event.get("type"), payload=event)

	etype = event.get("type")

	if etype == "checkout.session.completed":
		data = event.get("data", {}).get("object", {})
		metadata = data.get("metadata", {})
		payment_id = metadata.get("payment_id")
		purpose = metadata.get("purpose")
		reference_id = metadata.get("reference_id")
		payment_intent = data.get("payment_intent")
		if not payment_id:
			return HttpResponseBadRequest("Missing payment_id in metadata")

		payment = get_object_or_404(Payment, id=int(payment_id))
		if payment.status == Payment.STATUS_PAID:
			se.mark_processed()
			return HttpResponse(status=200)

		payment.status = Payment.STATUS_PAID
		if payment_intent:
			payment.stripe_payment_intent_id = payment_intent
		payment.save()

		# Create Receipt if not exists
		if not hasattr(payment, "receipt"):
			receipt = Receipt.objects.create(
				payment=payment,
				receipt_number=Receipt.generate_receipt_number(),
				billing_email=payment.user.email,
				amount_cents=payment.amount_cents,
				currency=payment.currency,
			)
		else:
			receipt = payment.receipt

		# Domain updates
		try:
			if purpose == Payment.PURPOSE_CLASSROOM_ENROLLMENT and reference_id:
				enr = Enrollment.objects.filter(id=int(reference_id)).first()
				if enr:
					enr.status = Enrollment.Status.ACTIVE
					enr.save(update_fields=["status"])
					# Ensure paid classroom users get student access.
					student_group, _ = Group.objects.get_or_create(name="estudiantes")
					enr.user.groups.add(student_group)
			elif purpose == Payment.PURPOSE_SHOP_ORDER and reference_id:
				from shop.models import Order
				ord = Order.objects.filter(id=int(reference_id)).first()
				if ord:
					ord.status = Order.Status.PAID
					ord.save(update_fields=["status"])
		except Exception:
			# Do not fail webhook for domain update issues
			pass

		# Email confirmation
		try:
			url = request.build_absolute_uri(receipt.get_absolute_url())
			send_payment_email(
				payment.user.email,
				subject=f"Pago confirmado – Recibo {receipt.receipt_number}",
				template_name="payments/email_confirmed.html",
				context={"message": f"Su pago fue confirmado. Recibo: {receipt.receipt_number}. Ver: {url}"},
			)
		except Exception:
			pass

		se.mark_processed()
		return HttpResponse(status=200)

	elif etype == "payment_intent.payment_failed":
		data = event.get("data", {}).get("object", {})
		intent_id = data.get("id")
		if intent_id:
			Payment.objects.filter(stripe_payment_intent_id=intent_id).update(status=Payment.STATUS_FAILED)
		se.mark_processed()
		return HttpResponse(status=200)

	elif etype == "charge.refunded":
		data = event.get("data", {}).get("object", {})
		payment_intent = data.get("payment_intent")
		Payment.objects.filter(stripe_payment_intent_id=payment_intent).update(status=Payment.STATUS_REFUNDED)
		# Optional domain revocation handled by apps as needed
		se.mark_processed()
		return HttpResponse(status=200)

	elif etype == "charge.dispute.created":
		data = event.get("data", {}).get("object", {})
		payment_intent = data.get("payment_intent")
		Payment.objects.filter(stripe_payment_intent_id=payment_intent).update(status=Payment.STATUS_DISPUTED)
		se.mark_processed()
		return HttpResponse(status=200)

	# Default: mark processed and ack
	se.mark_processed()
	return HttpResponse(status=200)

