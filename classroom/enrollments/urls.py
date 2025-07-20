# enrollments/urls.py

from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('', views.enrollment_list, name='enrollment-list'),
    path('<int:pk>/', views.enrollment_detail, name='enrollment-detail'),
    path('create/<int:course_id>/', views.enrollment_create, name='enrollment-create'),
    path('<int:pk>/delete/', views.enrollment_delete, name='enrollment-delete'),
    path('mark_module_complete/<int:module_id>/', views.mark_module_complete, name='mark_module_complete'),
    path('mark_lesson_complete/<int:lesson_id>/', views.mark_lesson_complete, name='mark_lesson_complete'),
]
