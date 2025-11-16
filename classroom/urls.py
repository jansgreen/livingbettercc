from django.urls import path, include


urlpatterns = [
    path('courses/', include('classroom.courses.urls')),
    path('enrollments/', include('classroom.enrollments.urls')),
    path('certifications/', include('classroom.certifications.urls')),
    path('quicktest/', include('classroom.quicktest.urls')),

]
