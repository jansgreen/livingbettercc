from django.urls import path
from .views import create_metadata
from django.views.generic.base import TemplateView


urlpatterns = [
    path('create/', create_metadata, name='create_metadata'),
    path('success/', TemplateView.as_view(template_name='metadata/success.html'), name='metadata_success'),  # Página de éxito
]
