from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:pk>/', views.profile_view, name='profile_detail'),
    path('profile/create/', views.profile_create_view, name='profile_create'),
    path('profile/list/', views.profile_list_view, name='profile_list'),
    path('profile/update/<int:pk>/', views.profile_update_view, name='profile_update'),
    path('profile/delete/<int:pk>/', views.profile_delete_view, name='profile_delete'),
   # Diferente tipos de usuarios
    #path('customer/', views.customer_view, name='customer_form'),
    # path('student/', views.student_view, name='student_form'),
    # path('staff/', views.staff_view, name='staff_form'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    #usuarios clientes
    path('customer_form/', views.customer_view, name='customer_form'),
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/create/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update_view, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),
]
