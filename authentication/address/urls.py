from django.urls import path, include
from . import views

app_name = 'address'

urlpatterns = [    # Address CRUD views
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/<int:pk>/', views.address_detail, name='address_detail'),
    path('addresses/create/<str:address_type>/<int:pk>/', views.address_create, name='address_create'),
    path('addresses/<int:pk>/update/', views.address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
]