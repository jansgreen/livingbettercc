from django.urls import path, include


urlpatterns = [
    path('courses/', include('classroom.courses.urls')),
    path('enrollments/', include('classroom.enrollments.urls')),
    path('certifications/', include('classroom.certifications.urls')),
    # Namespace quicktest so reverse('quicktest:...') works consistently
    path('quicktest/', include(('classroom.quicktest.urls', 'quicktest'), namespace='quicktest')),

]
