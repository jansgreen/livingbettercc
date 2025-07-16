from django.urls import path, include


urlpatterns = [
    path('courses/', include('classroom.courses.urls')),
    path('enrollments/', include('classroom.enrollments.urls')),

]
