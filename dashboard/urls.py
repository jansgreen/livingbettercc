from . import views
from django.urls import path, include
from dashboard import views

urlpatterns = [
    path('', views.dashboards, name='dashboard'),
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

    # app acopladas
    path('metadata/', include('dashboard.metadata.urls')),
    path('groups/', include('dashboard.groups.urls')),
    path('page/', include('dashboard.page.urls')),
    path('contents/', include('dashboard.contents.urls')),


]