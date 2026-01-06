from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from classroom.courses.models import Course
from classroom.enrollments.models import Enrollment, Payment

class PaymentFlowSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_owner = User.objects.create_user(username='owner', password='pass')
        self.user_other = User.objects.create_user(username='other', password='pass')
        self.course = Course.objects.create(title='Curso Pago', description='Desc', price=50)
        # Owner enrolls via course_enroll to set PENDING_PAYMENT
        self.client.login(username='owner', password='pass')
        enroll_url = reverse('courses:course_enroll', kwargs={'pk': self.course.pk})
        self.client.get(enroll_url)
        self.client.logout()
        self.enrollment = Enrollment.objects.get(user=self.user_owner, course=self.course)

    def test_pending_payment_shows_pay_button(self):
        self.client.login(username='owner', password='pass')
        my_course_url = reverse('courses:my_course')
        r = self.client.get(my_course_url)
        self.assertEqual(r.status_code, 200)
        self.assertIn('Pago pendiente', r.content.decode())
        # Pay button link to create_checkout_session
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': self.enrollment.id})
        self.assertIn(pay_url, r.content.decode())

    @patch('classroom.enrollments.views.stripe.checkout.Session.create')
    def test_owner_can_create_checkout_session(self, mock_create):
        # Mock stripe session creation
        mock_create.return_value = type('Obj', (), {'id': 'sess_123', 'url': 'https://checkout.stripe.com/test'})
        self.client.login(username='owner', password='pass')
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': self.enrollment.id})
        r = self.client.get(pay_url)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r['Location'], 'https://checkout.stripe.com/test')
        # Payment record created and linked
        p = Payment.objects.filter(enrollment=self.enrollment).first()
        self.assertIsNotNone(p)
        self.assertEqual(p.stripe_session_id, 'sess_123')

    def test_non_owner_cannot_create_checkout_session(self):
        self.client.login(username='other', password='pass')
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': self.enrollment.id})
        r = self.client.get(pay_url)
        self.assertEqual(r.status_code, 404)