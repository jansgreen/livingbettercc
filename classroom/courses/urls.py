from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('course_list/', views.course_list, name='course_list'),
    path('my_course/', views.my_course, name='my_course'),
    path('course_create/', views.course_create, name='course_create'),
    path('course_detail/<int:pk>/', views.course_detail, name='course_detail'),
    path('course_update/<int:pk>/', views.course_update, name='course_update'),
    path('course_delete/<int:pk>/', views.course_delete, name='course_delete'),

    # consultas Exequatur

    #Modules URLs
    path('module_create/', views.module_create, name='module_create'),
    path('module_list/', views.module_list, name='module_list'),
    path('module_update/<int:pk>/', views.module_update, name='module_update'),
    path('module_delete/<int:pk>/', views.module_delete, name='module_delete'),
    path('module_detail/<int:pk>/', views.module_detail, name='module_detail'),

    # Lessons URLs
    path('lesson_create/', views.lesson_create, name='lesson_create'),
    path('lesson_list/', views.lesson_list, name='lesson_list'),
    path('lesson_update/<int:pk>/', views.lesson_update, name='lesson_update'),
    path('lesson_delete/<int:pk>/', views.lesson_delete, name='lesson_delete'),
    path('lesson_detail/<int:pk>/', views.lesson_detail, name='lesson_detail'),

    # Tests URLs
    path('save_test_result/', views.save_test_result, name='save_test_result'),
    path('test_detail/<int:pk>/', views.test_detail, name='test_detail'),

    # Enroll
    path('course_enroll/<int:pk>/', views.course_enroll, name='course_enroll'),
]
