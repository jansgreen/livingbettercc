
from django.urls import path
from . import views

app_name = 'contents'

urlpatterns = [

    # Content Posts URLs
    path('content/ContentListView/', views.ContentListView, name='ContentListView'),
    path('content/ContentDetailView/<int:pk>/', views.ContentDetailView, name='ContentDetailView'),
    path('content/ContentCreateView/', views.ContentCreateView, name='ContentCreateView'),
    path('content/ContentUpdateView/<int:pk>/', views.ContentUpdateView, name='ContentUpdateView'),
    path('content/ContentDeleteView/<int:pk>/', views.ContentDeleteView, name='ContentDeleteView'),

    # Content Categories URLs
    path('categories/CategoryListView/', views.CategoryListView, name='CategoryListView'),
    path('categories/CategoryCreateView/', views.CategoryCreateView, name='CategoryCreateView'),
    path('categories/CategoryUpdateView/<int:pk>/', views.CategoryUpdateView, name='CategoryUpdateView'),
    path('categories/CategoryDeleteView/<int:pk>/', views.CategoryDeleteView, name='CategoryDeleteView'),

]
