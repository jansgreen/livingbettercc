from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from classroom.courses.models import Course
from classroom.enrollments.models import Enrollment
from payments.models import Payment, Receipt, StripeEvent


class PaymentsAppSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_owner = User.objects.create_user(username='owner', password='pass', email='owner@example.com')
        self.user_other = User.objects.create_user(username='other', password='pass')
        self.course = Course.objects.create(title='Curso Pago', description='Desc', price=50)
        self.client.login(username='owner', password='pass')
        enroll_url = reverse('courses:course_enroll', kwargs={'pk': self.course.pk})
        self.client.get(enroll_url)
        self.client.logout()
        self.enrollment = Enrollment.objects.get(user=self.user_owner, course=self.course)

    def test_owner_cannot_start_checkout_for_someone_else(self):
        self.client.login(username='other', password='pass')
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': self.enrollment.id})
        r = self.client.get(pay_url)
        self.assertEqual(r.status_code, 404)

    @patch('classroom.enrollments.views.stripe.checkout.Session.create')
    def test_start_checkout_creates_payment_and_redirects(self, mock_create):
        mock_create.return_value = type('Obj', (), {'id': 'sess_abc', 'url': 'https://checkout.stripe.com/test'})
        self.client.login(username='owner', password='pass')
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': self.enrollment.id})
        r = self.client.get(pay_url)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['Location'], 'https://checkout.stripe.com/test')
        # Generic payment exists
        gp = Payment.objects.filter(reference_id=str(self.enrollment.id), purpose=Payment.PURPOSE_CLASSROOM_ENROLLMENT).first()
        self.assertIsNotNone(gp)
        self.assertEqual(gp.stripe_session_id, 'sess_abc')
        # Legacy payment exists for compatibility
        from classroom.enrollments.models import Payment as LegacyPayment
        lp = LegacyPayment.objects.filter(enrollment=self.enrollment).first()
        self.assertIsNotNone(lp)
        self.assertEqual(lp.stripe_session_id, 'sess_abc')

    def test_receipt_access_restricted(self):
        # Create a paid payment and receipt
        p = Payment.objects.create(user=self.user_owner, amount_cents=5000, currency='usd', status=Payment.STATUS_PAID, provider='stripe', purpose=Payment.PURPOSE_CLASSROOM_ENROLLMENT, reference_id=str(self.enrollment.id))
        rcp = Receipt.objects.create(payment=p, receipt_number='LB-2026-000001', amount_cents=5000, currency='usd')
        # Owner can access
        self.client.login(username='owner', password='pass')
        url = reverse('payments:receipt_detail', kwargs={'receipt_number': rcp.receipt_number})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Other user forbidden
        self.client.logout()
        self.client.login(username='other', password='pass')
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 403)

    @patch('payments.views.stripe.Webhook.construct_event')
    def test_webhook_idempotency(self, mock_construct):
        # Prepare a Payment
        p = Payment.objects.create(user=self.user_owner, amount_cents=5000, currency='usd', status=Payment.STATUS_INITIATED, provider='stripe', purpose=Payment.PURPOSE_CLASSROOM_ENROLLMENT, reference_id=str(self.enrollment.id))
        # Stripe event payload
        payload = {
            'id': 'evt_test_1',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'sess_test',
                    'metadata': {
                        'payment_id': str(p.id),
                        'user_id': str(self.user_owner.id),
                        'purpose': Payment.PURPOSE_CLASSROOM_ENROLLMENT,
                        'reference_id': str(self.enrollment.id),
                    },
                    'payment_intent': 'pi_123',
                }
            }
        }
        import json
        mock_construct.return_value = payload
        # First attempt processes and marks paid
        r1 = self.client.post(reverse('payments:stripe_webhook'), data=json.dumps(payload), content_type='application/json', **{'HTTP_STRIPE_SIGNATURE': 'testsig'})
        self.assertEqual(r1.status_code, 200)
        # Simulate idempotency: record event and post again
        StripeEvent.objects.create(event_id='evt_test_1', event_type='checkout.session.completed')
        r2 = self.client.post(reverse('payments:stripe_webhook'), data=json.dumps(payload), content_type='application/json', **{'HTTP_STRIPE_SIGNATURE': 'testsig'})
        self.assertEqual(r2.status_code, 200)
