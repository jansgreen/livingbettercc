from django.urls import path
from .views import create_metadata, metadata_list, edit_metadata, delete_metadata
from django.views.generic.base import TemplateView


urlpatterns = [
    path('create/', create_metadata, name='create_metadata'),
    path('success/', TemplateView.as_view(template_name='metadata/success.html'), name='metadata_success'),  # Página de éxito
    path('metadata/', metadata_list, name='metadata_list'),
    path('metadata/edit/<int:metadata_id>/', edit_metadata, name='edit_metadata'),
    path('metadata/delete/<int:metadata_id>/', delete_metadata, name='delete_metadata'),
]
