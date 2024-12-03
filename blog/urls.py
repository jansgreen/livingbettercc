from . import views
from django.urls import path

urlpatterns = [
    path('', views.blog, name='blog'),
    path('post_list', views.post_list, name='post_list'),
    path('post_create/', views.post_create, name='post_create'),
    path('post_update/<int:pk>/', views.post_update, name='post_update'),
    path('delete/<int:pk>/', views.post_delete, name='post_delete'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('archive/<int:year>/<int:month>/', views.archive_posts, name='archive_posts'),

    path('post_detail/<int:pk>/', views.post_detail, name='post_detail'),


]