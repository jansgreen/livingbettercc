from .views import home, aboutUs, contactanos, BioUser, leerBio, single_page
from django.urls import path, include



urlpatterns = [
    path('', home, name='home'),
    path('aboutUs/', aboutUs, name='aboutUs'),
    path('contactanos/', contactanos, name='contactanos'),
    path('BioUser/<int:pk>', BioUser, name='BioUser'),
    path('leerBio/<int:pk>', leerBio, name='leerBio'),
    path('single_page/<int:pk>', single_page, name='single_page'), 



]

