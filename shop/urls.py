from django.urls import path, include
from . import views

urlpatterns = [
    path('product_list/', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('product_update/<int:pk>/', views.product_update, name='product_update'),
    path('product_delete/<int:pk>/', views.product_delete, name='product_delete'),
    #path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Category CRUD
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('subcategory/create/<int:category_id>/', views.subcategory_create, name='subcategory_create'),

    # Cart
	path('cart/', views.cart_summary, name="cart_summary"),
	path('add/<int:product_id>/<int:product_qty>', views.cart_add, name="add_to_cart"),
	path('delete/', views.cart_delete, name="cart_delete"),
	path('update/', views.cart_update, name="cart_update"),

    # Checkout
    path('checkout/', include('shop.checkout.urls')),
    path('thanks/', views.thanks, name="thanks"),
]
