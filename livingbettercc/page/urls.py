from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_footer, name='ver_footer'),
    path('footer/ver/', views.ver_footer, name='ver_footer'),
    path('footer/agregar/', views.agregar_footer, name='agregar_footer'),
]
