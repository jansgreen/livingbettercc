from django.urls import path
from . import views

app = 'gallery'

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('create/', views.image_create, name='image_create'),
    path('update/<int:pk>/', views.image_update, name='image_update'),
    path('delete/<int:pk>/', views.image_delete, name='image_delete'),
]
