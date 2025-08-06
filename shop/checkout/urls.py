from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('checkout_list/', views.checkout_list, name='checkout_list'),
    path('create/', views.checkout_create, name='checkout_create'),
]
