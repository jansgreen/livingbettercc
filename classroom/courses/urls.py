from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course-list'),
    path('create/', views.course_create, name='course-create'),
    path('courses/<int:pk>/', views.course_detail, name='course-detail'),
    path('courses/<int:pk>/update/', views.course_update, name='course-update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course-delete'),

    #Modules URLs
    path('modules/create/', views.module_create, name='module-create'),
    path('modules/', views.module_list, name='module-list'),
    path('modules/<int:pk>/update/', views.module_update, name='module-update'),
    path('modules/<int:pk>/delete/', views.module_delete, name='module-delete'),
    path('modules/<int:pk>/', views.module_detail, name='module-detail'),

    # Lessons URLs
    path('lessons/', views.lesson_list, name='lesson-list'),
    path('lessons/create/', views.lesson_create, name='lesson-create'),
    path('lessons/<int:pk>/update/', views.lesson_update, name='lesson-update'),
    path('lessons/<int:pk>/delete/', views.lesson_delete, name='lesson-delete'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson-detail'),

    # Tests URLs
    path('save-test-result/', views.save_test_result, name='save-test-result'),
    path('test/<int:pk>/', views.test_detail, name='test-detail'),
    
    # Enroll
    path('<int:pk>/enroll/', views.course_enroll, name='course-enroll'),
]
