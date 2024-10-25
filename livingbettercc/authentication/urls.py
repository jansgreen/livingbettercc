from django.urls import path
from . import views
from blog.views import crear_post

urlpatterns = [
    path('', views.ProfileFunction, name='ProfileFunction'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('login/', views.custom_login_view, name='login'),
    path('blog/',crear_post, name='blog'),

    path('ProfileFunction/', views.ProfileFunction, name='ProfileFunction'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    ]
