from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Category, Product

from .models import Order, OrderItem


class OrderViewsTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(email='one@example.com', password='test-password', mobile='01012345678')
		self.other_user = User.objects.create_user(email='two@example.com', password='test-password', mobile='01012345679')
		category = Category.objects.create(name='Audio')
		self.product = Product.objects.create(
			name='Headphones', description='Wireless headphones', price=Decimal('99.99'), stock=4,
			image=SimpleUploadedFile('headphones.jpg', b'image-data'), category=category,
		)
		self.order = Order.objects.create(
			user=self.user, shipping_full_name='One User', shipping_phone='01012345678',
			shipping_address='1 Main Street', shipping_city='Cairo', total=Decimal('199.98'),
		)
		OrderItem.objects.create(order=self.order, product=self.product, quantity=2, price_at_purchase=Decimal('99.99'))

	def test_anonymous_user_cannot_view_order_history(self):
		self.assertRedirects(self.client.get(reverse('orders:order_history')), '/accounts/login/?next=/orders/')

	def test_anonymous_user_cannot_view_order_detail(self):
		self.assertRedirects(self.client.get(reverse('orders:order_detail', args=[self.order.id])), f'/accounts/login/?next=/orders/{self.order.id}/')

	def test_logged_in_user_can_view_order_history(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('orders:order_history'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, f'Order #{self.order.id}')

	def test_order_history_contains_only_logged_in_users_orders(self):
		other_order = Order.objects.create(
			user=self.other_user, shipping_full_name='Two User', shipping_phone='01012345679',
			shipping_address='2 Main Street', shipping_city='Cairo', total=Decimal('10.00'),
		)
		self.client.force_login(self.user)
		response = self.client.get(reverse('orders:order_history'))
		self.assertContains(response, f'Order #{self.order.id}')
		self.assertNotContains(response, f'Order #{other_order.id}')

	def test_user_can_open_their_own_order(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
		self.assertEqual(response.status_code, 200)

	def test_order_detail_contains_product(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
		self.assertContains(response, self.product.name)

	def test_order_detail_contains_quantity(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
		self.assertContains(response, '2')

	def test_order_detail_contains_prices_and_total(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
		self.assertContains(response, '99.99')
		self.assertContains(response, '199.98')

	def test_user_cannot_view_another_users_order(self):
		self.client.force_login(self.other_user)
		response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
		self.assertEqual(response.status_code, 404)
