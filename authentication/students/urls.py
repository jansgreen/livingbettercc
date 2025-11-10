    # student CRUD views

from django.urls import path, include
from . import views

app_name = 'students'


urlpatterns = [

    # Vista del Admin con relacion a los estudiantes
    path('student_create_view/', views.student_create_view, name='student_create'),
    path('student_update_view/<int:pk>/', views.student_update_view, name='student_update'),
    path('student_delete_view/<int:pk>/', views.student_delete_view, name='student_delete'),
    path('student_list_view/', views.student_list_view, name='student_list_view'),

    # Estudiantes privados o por el distritos
    path('student_detail_view/<int:pk>/', views.student_detail_view, name='student_detail_view'),
    path('student_by_district/', views.student_by_district, name='student_by_district'),


]