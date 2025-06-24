from .views import home, quienes_somos, contactanos, single_page, view_bio
from django.urls import path



urlpatterns = [
    path('', home, name='home'),
    path('view_bio/<int:pk>/', view_bio, name='view_bio'),
    path('quienes_somos/', quienes_somos, name='quienes_somos'),
    path('contactanos/', contactanos, name='contactanos'),
    path('single_page/<int:pk>', single_page, name='single_page'), 

]

