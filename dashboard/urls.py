from . import views
from django.urls import path, include
from dashboard import views

urlpatterns = [
    path('dashboards/', views.dashboards, name='dashboards'),
    # menu paths
    path('menus', views.menu, name='menus'),
    path('categorias/', views.categoria_menu_list, name='categoria_menu_list'),
    path('categorias/create/', views.categoria_menu_create, name='categoria_menu_create'),
    path('categorias/<int:pk>/update/', views.categoria_menu_update, name='categoria_menu_update'),
    path('categorias/<int:pk>/delete/', views.categoria_menu_delete, name='categoria_menu_delete'),
    path('menuitems/', views.menuitem_list, name='menuitem_list'),
    path('menuitems/create/', views.menuitem_create, name='menuitem_create'),
    path('menuitems/<int:pk>/update/', views.menuitem_update, name='menuitem_update'),
    path('menuitems/<int:pk>/delete/', views.menuitem_delete, name='menuitem_delete'),
    path('metadata/', include('dashboard.metadata.urls')),

]