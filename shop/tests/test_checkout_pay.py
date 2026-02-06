from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Category, Product, Order, OrderItem

class CheckoutPayTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Libros', description='Cat', slug='libros')
        self.product = Product.objects.create(
            name='Libro 1', description='Contenido', price=10, stock=100, category=self.category
        )

    def _seed_cart_session(self, qty=1):
        s = self.client.session
        s['session_key'] = {str(self.product.id): int(qty)}
        s.save()

    def test_checkout_pay_creates_order_and_redirects_to_payments(self):
        user = User.objects.create_user(username='buyer', password='pass')
        self.client.login(username='buyer', password='pass')
        self._seed_cart_session(qty=2)

        r = self.client.get(reverse('shop:checkout:checkout_pay'))
        self.assertEqual(r.status_code, 302)

        order = Order.objects.filter(user=user).order_by('-id').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, Order.Status.PENDING_PAYMENT)
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)

        # Redirect should be to payments:start_order_checkout for this order
        target = reverse('payments:start_order_checkout', kwargs={'order_id': order.id})
        self.assertIn(target, r.headers.get('Location', ''))

        # Session should track last_order_id
        s = self.client.session
        self.assertEqual(s.get('last_order_id'), order.id)

    def test_checkout_pay_idempotent_reuses_pending_order(self):
        user = User.objects.create_user(username='buyer2', password='pass2')
        self.client.login(username='buyer2', password='pass2')
        self._seed_cart_session(qty=1)

        r1 = self.client.get(reverse('shop:checkout:checkout_pay'))
        self.assertEqual(r1.status_code, 302)
        order = Order.objects.filter(user=user).order_by('-id').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, Order.Status.PENDING_PAYMENT)

        # Call again; should reuse the same pending order via session
        r2 = self.client.get(reverse('shop:checkout:checkout_pay'))
        self.assertEqual(r2.status_code, 302)
        self.assertEqual(Order.objects.filter(user=user, status=Order.Status.PENDING_PAYMENT).count(), 1)

        target = reverse('payments:start_order_checkout', kwargs={'order_id': order.id})
        self.assertIn(target, r1.headers.get('Location', ''))
        self.assertIn(target, r2.headers.get('Location', ''))

    def test_checkout_pay_requires_login(self):
        # Seed cart without logging in
        self._seed_cart_session(qty=1)
        r = self.client.get(reverse('shop:checkout:checkout_pay'))
        self.assertEqual(r.status_code, 302)
        # login_required should redirect to accounts login with next
        self.assertIn('/accounts/login/', r.headers.get('Location', ''))
