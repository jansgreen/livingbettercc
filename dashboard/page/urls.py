from django.urls import path
from . import views

app_name = 'page'


urlpatterns = [

    path('footer', views.ver_footer, name='ver_footer'),
    path('footer/ver/', views.ver_footer, name='ver_footer'),
    path('footer/agregar/', views.agregar_footer, name='agregar_footer'),

    # Rutas para CRUD de Page, PageSection
    # --- PAGES ---
    path('', views.page_list, name='list'),
    path('create/', views.page_create, name='create'),
    path('<slug:slug>/', views.page_detail, name='detail'),
    path('<slug:slug>/edit/', views.page_update, name='update'),
    path('<slug:slug>/delete/', views.page_delete, name='delete'),

    # --- SECTIONS ---
    path('sections/sections_list/', views.section_list, name='sections_list'),
    path('sections/create/', views.section_create, name='sections_create'),
    path('sections_update/<int:pk>/', views.section_update, name='sections_update'),
    path('sections/<int:pk>/delete/', views.section_delete, name='sections_delete'),

    # Agrega las rutas para editar y eliminar categorias de imagenes
    path('carouselPageFunction/', views.carouselPageFunction, name='carouselPageFunction'),  # Listar habilidades
    path('image/<int:img_id>/eliminar/', views.imagen_delete, name='imagen_delete'),  # Eliminar imagen


]
