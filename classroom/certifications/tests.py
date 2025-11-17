from django.test import TestCase
from django.contrib.auth import get_user_model
from classroom.courses.models import Course
from .models import Certificate
from django.utils import timezone

class CertificateCRUDTest(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='testuser', password='testpass')
		self.course = Course.objects.create(title='Curso Test', published=True)

	def test_create_certificate(self):
		cert = Certificate.objects.create(
			user=self.user,
			course=self.course,
			certificate_number='CERT-1-1-20251116',
			issued_date=timezone.now().date(),
		)
		self.assertIsNotNone(cert.id)
		self.assertEqual(cert.user, self.user)
		self.assertEqual(cert.course, self.course)

	def test_read_certificate(self):
		cert = Certificate.objects.create(
			user=self.user,
			course=self.course,
			certificate_number='CERT-1-1-20251116',
			issued_date=timezone.now().date(),
		)
		found = Certificate.objects.get(pk=cert.id)
		self.assertEqual(found.certificate_number, 'CERT-1-1-20251116')

	def test_update_certificate(self):
		cert = Certificate.objects.create(
			user=self.user,
			course=self.course,
			certificate_number='CERT-1-1-20251116',
			issued_date=timezone.now().date(),
		)
		cert.certificate_number = 'CERT-UPDATED'
		cert.save()
		updated = Certificate.objects.get(pk=cert.id)
		self.assertEqual(updated.certificate_number, 'CERT-UPDATED')

	def test_delete_certificate(self):
		cert = Certificate.objects.create(
			user=self.user,
			course=self.course,
			certificate_number='CERT-1-1-20251116',
			issued_date=timezone.now().date(),
		)
		cert_id = cert.id
		cert.delete()
		with self.assertRaises(Certificate.DoesNotExist):
			Certificate.objects.get(pk=cert_id)
