from django.urls import path
from . import views


urlpatterns = [
    path('', views.ver_footer, name='ver_footer'),
    path('footer/ver/', views.ver_footer, name='ver_footer'),
    path('footer/agregar/', views.agregar_footer, name='agregar_footer'),
    path('create_page_content/', views.create_page_content, name='create_page_content'),

    path('manage-columns/', views.manage_columns, name='manage_columns'),
    path('edit-column/<int:column_id>/', views.edit_column, name='edit_column'),
    path('delete-column/<int:column_id>/', views.delete_column, name='delete_column'),
    path('page-content-list/', views.page_content_list, name='page_content_list'),
    path('manage-page-content/', views.manage_page_content, name='manage_page_content'),
    path('edit-page-content/<int:content_id>/', views.edit_page_content, name='edit_page_content'),
    path('delete-page-content/<int:content_id>/', views.delete_page_content, name='delete_page_content'),    
    # Agrega las rutas para editar y eliminar categorias de imagenes
    path('image/category/list', views.img_category_list, name='img_category_list'),  # Listar habilidades
    path('image/category/agregar/', views.img_category_create, name='img_category_create'),  # Crear habilidad
    path('image/category/<int:pk>/editar/', views.img_category_update, name='img_category_update'),  # Editar habilidad
    path('image/category/<int:pk>/eliminar/', views.img_category_delete, name='img_category_delete'),  # Eliminar habilidad

    path('image/<int:img_id>/agregar/', views.imagen_create, name='imagen_create'),  # Crear imagen
    path('image/<int:img_id>/eliminar/', views.imagen_delete, name='imagen_delete'),  # Eliminar imagen

    path('listar_categorias_y_columnas/', views.listar_categorias_y_columnas, name='listar_categorias_y_columnas'),
    path('crear_categoria/', views.crear_categoria, name='crear_categoria'),
    path('crear_columna/', views.crear_columna, name='crear_columna'), 
    path('delete_columna/<int:pk>/', views.delete_columna, name='delete_columna'),
    path('delete_pageCategorias/<int:pk>/', views.delete_pageCategorias, name='delete_pageCategorias'),

]
