from django.urls import path
from . import views

app_name = 'formbuilder'

urlpatterns = [
    # Legacy index alias
    path('', views.form_list, name='form_list_root'),

    # FormDefinition CRUD
    path('forms/', views.form_list, name='form_list'),
    path('forms/create/', views.form_create, name='form_create'),
    path('forms/<int:pk>/', views.form_detail, name='form_detail'),
    path('forms/<int:pk>/edit/', views.form_update, name='form_update'),
    path('forms/<int:pk>/delete/', views.form_delete, name='form_delete'),
    path('forms/assignments/', views.form_assignments, name='form_assignments'),
    path('forms/assignments/system/<str:system_key>/', views.form_assignments, name='system_form_assignments'),
    path('forms/<int:pk>/assignments/', views.form_assignments, name='form_assignments_for_form'),

    # FormField CRUD
    path('forms/<int:form_pk>/fields/add/', views.field_create, name='field_add'),
    path('fields/<int:pk>/edit/', views.field_update, name='field_update'),
    path('fields/<int:pk>/delete/', views.field_delete, name='field_delete'),

    # Render dynamic form
    path('render/<str:form_name>/', views.render_form, name='render_form'),
    path('render/id/<int:form_id>/', views.render_form_by_id, name='render_form_by_id'),

    # Facilitador flows
    path('facilitador/facilitador_list_view/', views.facilitador_list_view, name='facilitador_list_view'),
    path('facilitador/enroll_facilitador/', views.enroll_facilitador, name='enroll_facilitador'),
    path('facilitador/pending/', views.pending_forms, name='pending_forms'),
    path('facilitador/edit_forms/', views.edit_forms, name='edit_forms'),

    # Completed forms
    path('completed/', views.completed_forms_list, name='completed_forms_list'),
    path('completed/<int:pk>/', views.completed_forms_detail, name='completed_forms_detail'),
    path('completed/<int:pk>/edit/', views.completed_forms_edit, name='completed_forms_edit'),
    path('completed/<int:pk>/share/', views.share_with_facilitadores, name='share_with_facilitadores'),
    path('completed/shared/<int:pk>/', views.shared_completed_form, name='shared_completed_form'),
    path('completed/facilitadores_por_formulario/', views.facilitadores_por_formulario, name='facilitadores_por_formulario'),
    path('completed/my/', views.my_user_complete_forms, name='my_user_completed_forms'),

    # Share form definitions
    path('share/form/<int:pk>/', views.share_form_definition, name='share_form_definition'),
    path('share/s/<uuid:token>/', views.shared_form_definition, name='shared_form_definition'),
    path('shared/<uuid:token>/', views.shared_form_entry, name='shared_form_entry'),

    # Legacy aliases (avoid breaking existing links)
    path('create/', views.form_create, name='form_create_legacy'),
    path('<int:pk>/', views.form_detail, name='form_detail_legacy'),
    path('<int:pk>/update/', views.form_update, name='form_update_legacy'),
    path('<int:pk>/delete/', views.form_delete, name='form_delete_legacy'),
    path('<int:form_pk>/fields/add/', views.field_create, name='field_add_legacy'),
    path('fields/<int:pk>/update/', views.field_update, name='field_update_legacy'),
    path('fields/<int:pk>/delete/', views.field_delete, name='field_delete_legacy'),
    path('completed/completed_forms_list/', views.completed_forms_list, name='completed_forms_list_legacy'),
    path('completed/completed_forms_detail/<int:pk>/', views.completed_forms_detail, name='completed_forms_detail_legacy'),
    path('completed/completed_forms_edit/<int:pk>/edit/', views.completed_forms_edit, name='completed_forms_edit_legacy'),
    path('completed/my_user_complete_forms/', views.my_user_complete_forms, name='my_user_completed_forms_legacy'),

    # Tecnico panel (general and detail by center)
    
    path('tecnico/reporte_general/', views.tecnico_report_general, name='tecnico_report_general'),
    path('tecnico/<int:pk>/', views.tecnico_report_detail, name='tecnico_report_detail'),
    path('tecnico/panel/', views.panel_tecnico, name='panel_tecnico'),
    path('tecnico/panel/user/<int:user_id>/', views.panel_tecnico_user, name='panel_tecnico_user'),

]

