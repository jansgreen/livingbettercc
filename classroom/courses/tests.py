from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from classroom.courses.models import Course, Module, Lesson  # ajusta si tus modelos están en otro módulo

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
