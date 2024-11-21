from django.urls import path
from . import views


urlpatterns = [
    path('footer', views.ver_footer, name='ver_footer'),
    path('footer/ver/', views.ver_footer, name='ver_footer'),
    path('footer/agregar/', views.agregar_footer, name='agregar_footer'),
    path('create_page_content/', views.create_page_content, name='create_page_content'),

    path('manage-PagePosition/', views.manage_PagePosition, name='manage_PagePosition'),
    path('edit-PagePosition/<int:PagePosition_id>/', views.edit_PagePosition, name='edit_PagePosition'),
    path('delete-PagePosition/<int:PagePosition_id>/', views.delete_PagePosition, name='delete_PagePosition'),
    path('page-content-list/', views.page_content_list, name='page_content_list'),
    path('manage-page-content/', views.manage_page_content, name='manage_page_content'),
    path('edit-page-content/<int:content_id>/', views.edit_page_content, name='edit_page_content'),
    path('delete-page-content/<int:content_id>/', views.delete_page_content, name='delete_page_content'),    
    
    # Agrega las rutas para editar y eliminar categorias de imagenes
    path('carouselPageFunction/', views.carouselPageFunction, name='carouselPageFunction'),  # Listar habilidades
    path('image/<int:img_id>/eliminar/', views.imagen_delete, name='imagen_delete'),  # Eliminar imagen

    path('listar_categorias_y_PagePosition/', views.listar_categorias_y_PagePosition, name='listar_categorias_y_PagePosition'),
    path('crear_PageCategory/', views.crear_PageCategory, name='crear_PageCategory'),
    path('crear_PagePosition/', views.crear_PagePosition, name='crear_PagePosition'), 
    path('delete_PagePosition/<int:pk>/', views.delete_PagePosition, name='delete_PagePosition'),
    path('delete_pageCategorias/<int:pk>/', views.delete_pageCategorias, name='delete_pageCategorias'),

]
