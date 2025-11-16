from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboards, name='dashboard'),

    # app acopladas
    path('metadata/', include('dashboard.metadata.urls')),
    path('groups/', include('dashboard.groups.urls')),
    path('contents/', include('dashboard.contents.urls')),

    # Listado de aplicaciones a beca Minerd
    path('beca-applications/', views.beca_applications_list, name='beca_applications_list'),
    path('beca-applications/action/<int:app_id>/', views.beca_application_action, name='beca_application_action'),
]