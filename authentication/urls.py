from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('login/', views.custom_login_view, name='login'),

    path('ProfileFunction/', views.ProfileFunction, name='ProfileFunction'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_biography/', views.edit_biography, name='edit_biography'),

    ]
