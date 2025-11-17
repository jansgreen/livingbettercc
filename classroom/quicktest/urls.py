from django.urls import path
from . import views

app_name = 'quicktest'

urlpatterns = [
    path('', views.quicktest_list, name='quicktest_list'),
    path('<int:pk>/', views.quicktest_detail, name='quicktest_detail'),
    path('create/<int:module_id>/', views.quicktest_create, name='quicktest_create'),
]
