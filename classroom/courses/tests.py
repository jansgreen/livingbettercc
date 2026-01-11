from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory

from classroom.courses.models import Course, Module, Lesson
from classroom.enrollments.models import Enrollment, LessonCompletion
from classroom.quicktest.models import QuickTestDefinition, QuickTest
from classroom.certifications.models import Certificate
from classroom.courses.views import next_module, quicktest_view


class CourseFlowTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="u1", email="u1@example.com", password="pass")
        self.client.login(username="u1", password="pass")
        self.factory = RequestFactory()

        # Create a simple course with two modules and lessons
        self.course = Course.objects.create(title="Curso X", price=0)
        self.mod1 = Module.objects.create(course=self.course, title="M1", order=1)
        self.mod2 = Module.objects.create(course=self.course, title="M2", order=2)

        # Lessons for each module
        self.l1 = Lesson.objects.create(module=self.mod1, title="L1", order=1)
        self.l2 = Lesson.objects.create(module=self.mod1, title="L2", order=2)
        self.l3 = Lesson.objects.create(module=self.mod2, title="L3", order=1)

        # Enrollment ACTIVE for user and course
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course, status=Enrollment.Status.ACTIVE)

    def _attach_messages(self, request):
        # attach message storage to request for view functions using messages
        setattr(request, 'session', self.client.session)
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

    def test_quicktest_view_requires_lessons_completed(self):
        # Define a quicktest for mod1, but don't complete all lessons
        QuickTestDefinition.objects.create(module=self.mod1)

        url = reverse('courses:quicktest', kwargs={'module_id': self.mod1.id})
        resp = self.client.get(url)
        # Should redirect to module_detail until all lessons completed
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('courses:module_detail', kwargs={'pk': self.mod1.id}), resp['Location'])

        # Mark lessons completed
        LessonCompletion.objects.create(enrollment=self.enrollment, lesson=self.l1)
        LessonCompletion.objects.create(enrollment=self.enrollment, lesson=self.l2)

        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

    def test_next_module_requires_quicktest_pass_and_redirects_to_test(self):
        # mod1 has quicktest but user hasn't passed yet
        QuickTestDefinition.objects.create(module=self.mod1)

        request = self.factory.get(reverse('courses:next_module', kwargs={'module_id': self.mod1.id}))
        request.user = self.user
        self._attach_messages(request)

        response = next_module(request, module_id=self.mod1.id)
        # Expect redirect to quicktest for mod1
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('courses:quicktest', kwargs={'module_id': self.mod1.id}), response['Location'])

        # Now pass quicktest
        QuickTest.objects.update_or_create(user=self.user, module=self.mod1, defaults={'score': 95})
        response2 = next_module(request, module_id=self.mod1.id)
        # Should go to next module detail
        self.assertEqual(response2.status_code, 302)
        self.assertIn(reverse('courses:module_detail', kwargs={'pk': self.mod2.id}), response2['Location'])

    def test_next_module_final_module_completes_enrollment_and_issues_certificate(self):
        # Both modules have quicktests and are passed
        QuickTestDefinition.objects.create(module=self.mod1)
        QuickTestDefinition.objects.create(module=self.mod2)
        QuickTest.objects.update_or_create(user=self.user, module=self.mod1, defaults={'score': 90})
        QuickTest.objects.update_or_create(user=self.user, module=self.mod2, defaults={'score': 85})

        # Call next_module on final module
        request = self.factory.get(reverse('courses:next_module', kwargs={'module_id': self.mod2.id}))
        request.user = self.user
        self._attach_messages(request)

        response = next_module(request, module_id=self.mod2.id)
        self.assertEqual(response.status_code, 302)

        # Enrollment should be marked completed
        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.completed)

        # Certificate should exist and have uuid
        cert = Certificate.objects.filter(user=self.user, course=self.course).first()
        self.assertIsNotNone(cert)
        self.assertTrue(bool(getattr(cert, 'uuid', None)))

    def test_lesson_detail_requires_active_enrollment(self):
        # Make enrollment inactive to test access restriction
        self.enrollment.status = Enrollment.Status.PENDING_PAYMENT
        self.enrollment.save(update_fields=['status'])

        url = reverse('courses:lesson_detail', kwargs={'pk': self.l1.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('courses:my_course'), resp['Location'])
