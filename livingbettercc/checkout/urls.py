from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('confirmar_pago/', views.confirmar_pago, name='confirmar_pago'),
    path('cancelar_pago/', views.cancelar_pago, name='cancelar_pago'),
    path('confirmacion_orden/', views.confirmacion_orden, name='confirmacion_orden'),
    
    ]