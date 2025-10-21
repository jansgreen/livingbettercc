    # student CRUD views

from django.urls import path, include
from . import views

app_name = 'minerd'

urlpatterns = [
    path('report_account_miner/create/', views.report_account_miner_create, name='report_account_miner_create'),
    path('report_account_miner/', views.report_account_miner_list, name='report_account_miner_list'),
    path('report_account_miner/update/<int:pk>/', views.report_account_miner_update, name='report_account_miner_update'),
    path('report_account_miner/delete/<int:pk>/', views.report_account_miner_delete, name='report_account_miner_delete'),
    path('report_account_miner/detail/<int:pk>/', views.report_account_miner_detail, name='report_account_miner_detail'),
]

