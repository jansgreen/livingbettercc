from .views import home, aboutUs, contactanos, BioUser, leerBio
from django.urls import path, include



urlpatterns = [
    path('', home, name='home'),
    path('aboutUs/', aboutUs, name='aboutUs'),
    path('contactanos/', contactanos, name='contactanos'),
    path('BioUser/<int:pk>', BioUser, name='BioUser'),
    path('leerBio/<int:pk>', leerBio, name='leerBio'),



]

