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
    path('curso/update/<int:curso_id>/', views.curso_update, name='curso_update'),
    path('curso/delete/<int:curso_id>/', views.curso_delete, name='curso_delete'),
    path('curso/list/', views.curso_list, name='curso_list'),
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module_detail'),
    path('modules/new/', ModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:pk>/edit/', ModuleUpdateView.as_view(), name='module_update'),
    path('modules/<int:pk>/delete/', ModuleDeleteView.as_view(), name='module_delete'),
]
