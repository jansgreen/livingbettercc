from django.urls import path, include
from . import views

app_name = 'authentication'

urlpatterns = [
    path('facilitador_register/', views.facilitador_register_view, name='facilitador_register'),
    path('tecnico_register/', views.tecnico_register_view, name='tecnico_register'),
    path('profile/', views.profile_view, name='profile_detail'),
    path('profile/create/', views.profile_create_view, name='profile_create'),
    path('profile/list/', views.profile_list_view, name='profile_list'),
    path('profile/update/<int:pk>/', views.profile_update_view, name='profile_update'),
    path('profile/delete/<int:pk>/', views.profile_delete_view, name='profile_delete'),
   # Registro de usuarios y 

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Aqui identifico la categoria a la que se le asignara al usuario
    path('prepare_register/<int:pk>/<str:role>/', views.prepare_register, name='prepare_register'),

    #usuarios clientes
    path('customer_form/', views.customer_view, name='customer_form'),
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/create/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update_view, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),

    # Address CRUD views
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/<int:pk>/', views.address_detail, name='address_detail'),
    path('addresses/create/<str:address_type>/<int:pk>/', views.address_create, name='address_create'),
    path('addresses/<int:pk>/update/', views.address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),

    # Directives CRUD views
    path('directives/', views.directives_list, name='directives_list'),
    path('directives/create/', views.directives_create, name='directives_create'),
    path('directives/<int:pk>/edit/', views.directives_update, name='directives_update'),
    path('directives/<int:pk>/delete/', views.directives_delete, name='directives_delete'),
    
    # students registration
    path('students/', include('authentication.students.urls')),
    path('address/', include('authentication.address.urls')),

]
