from django.urls import path
from . import views

app_name = 'formbuilder'

urlpatterns = [
    path('', views.form_list, name='form_list'),
    path('create/', views.form_create, name='form_create'),
    path('<int:pk>/', views.form_detail, name='form_detail'),
    path('<int:pk>/update/', views.form_update, name='form_update'),
    path('<int:pk>/delete/', views.form_delete, name='form_delete'),

    # FormField CRUD
    path('<int:form_pk>/fields/add/', views.field_create, name='field_add'),
    path('fields/<int:pk>/update/', views.field_update, name='field_update'),
    path('fields/<int:pk>/delete/', views.field_delete, name='field_delete'),
    path('<str:form_name>/', views.render_form, name='render_form'),

    # Completed Forms Views
    path('completed/completed_forms/', views.completed_forms_list, name='completed_forms_list'),
    path('completed/completed_forms_detail/<int:pk>/', views.completed_forms_detail, name='completed_forms_detail'),
    path('completed/completed_forms_edit/<int:pk>/edit/', views.completed_forms_edit, name='completed_forms_edit'),
    path('completed/completed_all_forms/', views.completed_all_forms_list, name='completed_all_forms_list'),
]

