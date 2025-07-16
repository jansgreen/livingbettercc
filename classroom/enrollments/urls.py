# enrollments/urls.py

from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('', views.enrollment_list, name='enrollment-list'),
    path('<int:pk>/', views.enrollment_detail, name='enrollment-detail'),
    path('create/<int:course_id>/', views.enrollment_create, name='enrollment-create'),
    path('<int:pk>/delete/', views.enrollment_delete, name='enrollment-delete'),
]
