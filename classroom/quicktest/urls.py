from django.urls import path
from . import views

app_name = 'quicktest'

urlpatterns = [
    path('', views.quicktest_list, name='quicktest_list'),
    path('create/<int:module_id>/', views.quicktest_create, name='quicktest_create'),
]
