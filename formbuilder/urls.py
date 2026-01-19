from django.urls import path
from . import views

app_name = 'formbuilder'

urlpatterns = [
    # crear plantilla de formulario
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

    # Completed Forms Views - All Users
    path('facilitador/facilitador_list_view/', views.facilitador_list_view, name='facilitador_list_view'),
    path('facilitador/enroll_facilitador/', views.enroll_facilitador, name='enroll_facilitador'),
    path("facilitador/pending/", views.pending_forms, name="pending_forms"),
    path('facilitador/edit_forms/', views.edit_forms, name='edit_forms'),

    # Completed Forms Views
    path('completed/completed_forms_list/', views.completed_forms_list, name='completed_forms_list'),
    path('completed/completed_forms_detail/<int:pk>/', views.completed_forms_detail, name='completed_forms_detail'),
    path('completed/completed_forms_edit/<int:pk>/edit/', views.completed_forms_edit, name='completed_forms_edit'),
    path('completed/<int:pk>/share/', views.share_with_facilitadores, name='share_with_facilitadores'),
    path('completed/shared/<int:pk>/', views.shared_completed_form, name='shared_completed_form'),
    path('completed/facilitadores_por_formulario/', views.facilitadores_por_formulario, name='facilitadores_por_formulario'),
    path('completed/my_user_complete_forms/', views.my_user_complete_forms, name='my_user_completed_forms'),

    # Share completed forms with facilitators
<<<<<<< HEAD
    # formbuilder/urls.py
=======
    path("share/form/<int:pk>/", views.share_form_definition, name="share_form_definition"),
    path("s/<uuid:token>/", views.shared_form_definition, name="shared_form_definition"),
    path("shared/<uuid:token>/", views.shared_form_entry, name="shared_form_entry"),
>>>>>>> dev

]

