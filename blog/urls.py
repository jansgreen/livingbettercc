from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_posts, name='listar_posts'),
    path('<int:pk>/', views.detalle_post, name='detalle_post'),
    path('bio/nuevo/', views.crear_post_Bio, name='crear_post_Bio'),
    path('post/nuevo/', views.crear_post, name='crear_post'),
    path('<int:pk>/editar/', views.actualizar_post, name='actualizar_post'),
    path('<int:pk>/eliminar/', views.eliminar_post, name='eliminar_post'),
    path('categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('actualizar/categoria/<int:pk>', views.actualizar_categoria, name='actualizar_categoria'),
    path('actualizar/posicion/<int:pk>', views.actualizar_posicion, name='actualizar_posicion'),
    path('posiciones/nueva/', views.crear_posicion, name='crear_posicion'),
    
    ]
