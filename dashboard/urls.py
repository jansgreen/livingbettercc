from . import views
from django.urls import path, include
from dashboard import views

urlpatterns = [
    path('', views.dashboards, name='dashboard'),
 
    # app acopladas
    path('metadata/', include('dashboard.metadata.urls')),
    path('groups/', include('dashboard.groups.urls')),
    path('contents/', include('dashboard.contents.urls')),


]