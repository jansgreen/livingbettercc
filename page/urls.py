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
    # Agrega las rutas para editar y eliminar PageContent

]
