from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('login/', views.custom_login_view, name='login'),
    path('ProfileFunction/', views.ProfileFunction, name='ProfileFunction'),
    path('direccion/', views.direccion, name='direccion'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    path('leerBio/<int:pk>', views.leerBio, name='leerBio'),
    path('edit_biography/', views.edit_biography, name='edit_biography'),
    path('actualizar_direccion/<int:direccion_id>/', views.actualizar_direccion, name='actualizar_direccion'),
    path('eliminar_direccion/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),


    ]
