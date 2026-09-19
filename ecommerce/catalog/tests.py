from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import User

from .models import Category, Product


class CategoryManagementTests(TestCase):
	def setUp(self):
		self.staff = User.objects.create_user(
			email='staff@example.com',
			password='test-password',
			mobile='01012345678',
			is_staff=True,
		)
		self.category = Category.objects.create(name='Audio')

	def test_category_management_requires_staff(self):
		response = self.client.get('/catalog/manage/categories/')

		self.assertEqual(response.status_code, 302)
		self.assertIn('/admin/login/', response.url)

	def test_staff_can_add_category(self):
		self.client.force_login(self.staff)

		response = self.client.post(
			'/catalog/manage/categories/add/',
			{'name': 'Cameras', 'description': 'Photo equipment'},
		)

		self.assertRedirects(response, '/catalog/manage/categories/')
		self.assertTrue(Category.objects.filter(name='Cameras').exists())

	def test_delete_protected_category_shows_error(self):
		Product.objects.create(
			name='Headphones',
			description='Wireless headphones',
			price='99.99',
			stock=4,
			image=SimpleUploadedFile('headphones.jpg', b'image-data'),
			category=self.category,
		)
		self.client.force_login(self.staff)

		response = self.client.post(
			f'/catalog/manage/categories/{self.category.pk}/delete/'
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'cannot be deleted')
		self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
