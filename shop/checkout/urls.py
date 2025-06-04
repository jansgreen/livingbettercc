from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout_list, name='checkout_list'),
    path('create/', views.checkout_create, name='checkout_create'),
]
