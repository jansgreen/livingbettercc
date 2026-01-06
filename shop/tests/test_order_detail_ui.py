from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Category, Product, Order, OrderItem
from payments.models import Payment, Receipt


class OrderDetailUITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buyer', password='pass')
        self.category = Category.objects.create(name='Libros', description='Cat', slug='libros')
        self.product = Product.objects.create(
            name='Libro 1', description='Contenido', price=10, stock=100, category=self.category
        )

    def test_order_detail_shows_pay_button_when_pending(self):
        self.client.login(username='buyer', password='pass')
        order = Order.objects.create(user=self.user, status=getattr(Order.Status, 'PENDING_PAYMENT', 'pending_payment'))
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price=self.product.price)

        url = reverse('shop:order_detail', kwargs={'order_id': order.id})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        pay_url = reverse('payments:start_order_checkout', kwargs={'order_id': order.id})
        html = r.content.decode('utf-8')
        self.assertIn(pay_url, html)
        self.assertIn('Pagar', html)

    def test_order_detail_shows_receipt_when_paid(self):
        self.client.login(username='buyer', password='pass')
        order = Order.objects.create(user=self.user, status=getattr(Order.Status, 'PAID', 'paid'))

        payment = Payment.objects.create(
            purpose='shop_order',
            reference_id=str(order.id),
            status='paid'
        )
        receipt = Receipt.objects.create(payment=payment)

        url = reverse('shop:order_detail', kwargs={'order_id': order.id})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        receipt_url = reverse('payments:receipt_detail', kwargs={'receipt_number': receipt.receipt_number})
        html = r.content.decode('utf-8')
        self.assertIn(receipt_url, html)
        self.assertIn('Ver recibo', html)
