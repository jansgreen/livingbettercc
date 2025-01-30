from django.urls import path
from . import views
from .views import (
    ModuleListView,
    ModuleDetailView,
    ModuleCreateView,
    ModuleUpdateView,
    ModuleDeleteView,
)

urlpatterns = [
    path('curso/<int:curso_id>/', views.curso_principal, name='curso_principal'),
    path('leccion/<int:leccion_id>/', views.leccion_detalle, name='leccion_detalle'),
    path('curso/admin/', views.admin_panel, name='admin_panel'),
    path('curso/create/', views.curso_create, name='curso_create'),
    path('curse/update/<int:curso_id>/', views.curso_update, name='course_edit'),
    path('curso/delete/<int:curso_id>/', views.curso_delete, name='course_delete'),
    path('curso/list/', views.curso_list, name='course_detail'),
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module_detail'),
    path('modules/new/', ModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:pk>/edit/', ModuleUpdateView.as_view(), name='module_update'),
    path('modules/<int:pk>/delete/', ModuleDeleteView.as_view(), name='module_delete'),
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/edit/', views.lesson_update, name='lesson_update'),
    path('lessons/<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/edit/', views.material_update, name='material_update'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
]
