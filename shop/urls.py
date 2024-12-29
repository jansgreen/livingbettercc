from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('product_update/<int:pk>/', views.product_update, name='product_update'),
    path('product_delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("process-payment/<int:order_id>/", views.process_cardnet_payment, name="process_payment"),

    # Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Cart
	path('cart/', views.cart_summary, name="cart_summary"),
	path('add/', views.cart_add, name="cart_add"),
	path('delete/', views.cart_delete, name="cart_delete"),
	path('update/', views.cart_update, name="cart_update"),


]
