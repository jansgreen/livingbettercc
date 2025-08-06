    # student CRUD views

from django.urls import path, include
from . import views

app_name = 'students'


urlpatterns = [

    path('student_create_view/', views.student_create_view, name='student_create'),
    path('student_update_view/<int:pk>/', views.student_update_view, name='student_update'),
    path('student_delete_view/<int:pk>/', views.student_delete_view, name='student_delete'),
    path('student_register_view/', views.student_register_view, name='student_register_view'),
    path('student_district_view/<int:pk>/', views.student_district_view, name='student_district_view'),
    path('student_by_district/', views.student_by_district, name='student_by_district'),

]