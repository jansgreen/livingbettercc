from django.urls import path
from . import views

app_name = 'quicktest'

urlpatterns = [
    # Student results (existing minimal endpoints)
    path('', views.quicktest_list, name='quicktest_list'),
    path('<int:pk>/', views.quicktest_detail, name='quicktest_detail'),
    path('create/<int:module_id>/', views.quicktest_create, name='quicktest_create'),
    path('update/<int:pk>/', views.quicktest_update, name='quicktest_update'),
    path('delete/<int:pk>/', views.quicktest_delete, name='quicktest_delete'),

    # Staff CRUD for QuickTestDefinition
    path('definitions/', views.qdef_list, name='qdef_list'),
    path('definitions/create/', views.qdef_create, name='qdef_create'),
    path('definitions/<int:pk>/update/', views.qdef_update, name='qdef_update'),
    path('definitions/<int:pk>/delete/', views.qdef_delete, name='qdef_delete'),

    # Staff CRUD for QuickTestQuestion
    path('definitions/<int:def_id>/questions/', views.q_list, name='q_list'),
    path('definitions/<int:def_id>/questions/create/', views.q_create, name='q_create'),
    path('questions/<int:pk>/update/', views.q_update, name='q_update'),
    path('questions/<int:pk>/delete/', views.q_delete, name='q_delete'),
]
