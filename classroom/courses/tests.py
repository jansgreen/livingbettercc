from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from classroom.courses.models import Course, Module, Lesson  # ajusta si tus modelos están en otro módulo
from authentication.models.profiles import Profiles
from classroom.enrollments.models import Enrollment, BecaApplication

class LessonCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.course = Course.objects.create(title='Curso de prueba', description='Descripción')
        self.module = Module.objects.create(course=self.course, title='Módulo de prueba', order=1)
        self.lesson_create_url = reverse('courses:lesson_create')
        self.lesson_list_url = reverse('courses:lesson_list')

    def test_get_lesson_create_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.lesson_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson/lesson_form.html')

    def test_post_valid_lesson_create(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.lesson_create_url, {
            'title': 'Lección 1',
            'description': 'Contenido de prueba',
            'order': 1,
            'module_id': self.module.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('courses:lesson_list', kwargs={'pk': Lesson.objects.last().pk}))
        self.assertEqual(Lesson.objects.count(), 1)
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.title, 'Lección 1')
        self.assertEqual(lesson.module, self.module)

    def test_post_invalid_lesson_create(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.lesson_create_url, {
            'title': '',  # título requerido
            'description': '',
            'order': '',
            'module_id': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'title', 'Este campo es obligatorio.')
        self.assertEqual(Lesson.objects.count(), 0)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.lesson_create_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.lesson_create_url}')


class BecaFlowSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(title='Curso Beca', description='Desc', price=100)
        self.course_detail_url = reverse('courses:course_detail', kwargs={'pk': self.course.pk})
        self.enroll_url = reverse('courses:course_enroll', kwargs={'pk': self.course.pk})

    def _beca_payload(self):
        return {
            'enroll_type': 'beca',
            'cedula': '00112233445',
            'exequatur': 'EX-123',
            'centro_educativo': 'Colegio ABC',
            'distrito_escolar': 'Distrito 01',
            'street': 'Calle 1',
            'neighborhood': 'Barrio',
            'provincia': 'Provincia',
            'municipio': 'Municipio',
            'zip_code': '10000',
            'city': 'Ciudad',
            'state': 'Estado',
        }

    def test_unauthenticated_beca_flow(self):
        # Open course detail
        r1 = self.client.get(self.course_detail_url)
        self.assertEqual(r1.status_code, 200)
        # Submit beca
        r2 = self.client.post(self.enroll_url, data=self._beca_payload())
        # Redirect to register
        self.assertEqual(r2.status_code, 302)
        self.assertIn('authentication/register', r2.headers.get('Location', ''))
        # Session keys saved
        session = self.client.session
        self.assertIn('pending_beca', session)
        self.assertEqual(session.get('selected_item'), self.course.pk)
        # Create user and login to trigger reanudation
        user = User.objects.create_user(username='user1', password='pass1', email='u1@test.local')
        login_url = reverse('authentication:login')
        r3 = self.client.post(login_url, data={'username': 'user1', 'password': 'pass1'})
        self.assertEqual(r3.status_code, 302)
        # Verify BecaApplication and Enrollment
        self.assertEqual(BecaApplication.objects.filter(user=user, course=self.course).count(), 1)
        enr = Enrollment.objects.get(user=user, course=self.course)
        self.assertEqual(enr.status, Enrollment.Status.PENDING_APPROVAL)

    def test_authenticated_without_profile_redirects_to_profile_create(self):
        user = User.objects.create_user(username='user2', password='pass2')
        self.client.login(username='user2', password='pass2')
        r = self.client.post(self.enroll_url, data=self._beca_payload())
        self.assertEqual(r.status_code, 302)
        # Should redirect to profile creation
        self.assertIn(reverse('authentication:profile_create'), r.headers.get('Location', ''))
        # No BecaApplication yet
        self.assertEqual(BecaApplication.objects.filter(user=user, course=self.course).count(), 0)

    def test_authenticated_with_profile_creates_beca_and_pending_approval(self):
        user = User.objects.create_user(username='user3', password='pass3', email='u3@test.local')
        Profiles.objects.create(user=user, telefono='8090000000')
        self.client.login(username='user3', password='pass3')
        r = self.client.post(self.enroll_url, data=self._beca_payload())
        self.assertEqual(r.status_code, 302)
        # BecaApplication created
        beca = BecaApplication.objects.filter(user=user, course=self.course).first()
        self.assertIsNotNone(beca)
        self.assertEqual(beca.status, 'submitted')
        # Enrollment pending approval
        enr = Enrollment.objects.get(user=user, course=self.course)
        self.assertEqual(enr.status, Enrollment.Status.PENDING_APPROVAL)
        # Trying to access a module should be blocked (middleware redirects)
        mod = Module.objects.create(course=self.course, title='M1', order=1)
        mod_detail_url = reverse('courses:module_detail', kwargs={'pk': mod.pk})
        r2 = self.client.get(mod_detail_url)
        self.assertEqual(r2.status_code, 302)

    def test_idempotent_double_submit(self):
        user = User.objects.create_user(username='user4', password='pass4')
        Profiles.objects.create(user=user, telefono='8090000000')
        self.client.login(username='user4', password='pass4')
        payload = self._beca_payload()
        r1 = self.client.post(self.enroll_url, data=payload)
        r2 = self.client.post(self.enroll_url, data=payload)
        self.assertEqual(r1.status_code, 302)
        self.assertEqual(r2.status_code, 302)
        # No duplicate BecaApplication
        self.assertEqual(BecaApplication.objects.filter(user=user, course=self.course).count(), 1)
        # No duplicate Enrollment and remains pending approval
        self.assertEqual(Enrollment.objects.filter(user=user, course=self.course).count(), 1)
        self.assertEqual(Enrollment.objects.get(user=user, course=self.course).status, Enrollment.Status.PENDING_APPROVAL)

    def test_start_course_payment_sets_pending_and_redirects_to_checkout(self):
        # Paid course
        course = Course.objects.create(title='Pago Inmediato', description='Desc', price=150)
        user = User.objects.create_user(username='payer', password='paypass', email='p@test.local')
        Profiles.objects.create(user=user, telefono='8091112222')
        self.client.login(username='payer', password='paypass')
        url = reverse('courses:start_course_payment', kwargs={'pk': course.pk})
        r = self.client.get(url)
        self.assertEqual(r.status_code, 302)
        # Enrollment created and pending payment
        enr = Enrollment.objects.get(user=user, course=course)
        self.assertEqual(enr.status, Enrollment.Status.PENDING_PAYMENT)
        # Redirect to enrollments:create_checkout_session
        target_prefix = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': enr.id})
        self.assertIn(target_prefix, r.headers.get('Location', ''))
