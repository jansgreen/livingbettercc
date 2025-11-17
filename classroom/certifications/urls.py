# urls.py
from django.urls import path
from . import views

app_name = 'certifications'

urlpatterns = [
    path('list/', views.listar_certificados, name='certificate_list'),
    path('certificate/<uuid:uuid>/', views.certificate_public_view, name='certificate_public_view'),
    path('certificate/<uuid:uuid>/download/', views.certificate_pdf_download, name='certificate_pdf_download'),
]
