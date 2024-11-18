from .views import home, quienes_somos, contactanos, BioUser, leerBio, single_page
from django.urls import path, include



urlpatterns = [
    path('', home, name='home'),
    path('quienes_somos/', quienes_somos, name='quienes_somos'),
    path('contactanos/', contactanos, name='contactanos'),
    path('BioUser/<int:pk>', BioUser, name='BioUser'),
    path('leerBio/<int:pk>', leerBio, name='leerBio'),
    path('single_page/<int:pk>', single_page, name='single_page'), 



]

