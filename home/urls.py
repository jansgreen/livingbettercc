from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('view_bio/<int:pk>/', views.view_bio, name='view_bio'),
    path('quienes_somos/', views.quienes_somos, name='quienes_somos'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('single_page/<int:pk>', views.single_page, name='single_page'), 

    # Reportes de actividades CRUD
    path('report_activity/new/', views.report_create, name='report_create'),
    path('report_activity/<int:pk>/delete/', views.report_delete, name='report_delete'),
    path('report_activity/<int:pk>/', views.report_detail, name='report_detail'),
    path('report_activity/', views.report_list, name='report_list'),
    path('report_activity/<int:pk>/edit/', views.report_update, name='report_update'),

    # Categoria de los Reportes de Actividades CRUD
    path('report_categories/new/', views.report_categories_create, name='report_categories_create'),
    path('report_categories/<int:pk>/delete/', views.report_categories_delete, name='report_categories_delete'),
    path('report_categories/<int:pk>/', views.report_categories_detail, name='report_categories_detail'),
    path('report_categories/', views.report_categories_list, name='report_categories_list'),
    path('report_categories/<int:pk>/edit/', views.report_categories_update, name='report_categories_update'),

]

