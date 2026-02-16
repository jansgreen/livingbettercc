# urls.py
from django.urls import path
from . import views

app_name = 'certifications'

urlpatterns = [

    # CRUD for certificates admin/staff views
    path('certificate/new/', views.CertificateCreateView.as_view(), name='certificate_create'),
    path('certificate/<int:pk>/edit/', views.CertificateUpdateView.as_view(), name='certificate_edit'),
    path('certificate/<int:pk>/delete/', views.CertificateDeleteView.as_view(), name='certificate_delete'),
   
    # UUID-based aliases used by templates
    path('certificate/<uuid:uuid>/edit/', views.CertificateUpdateByUUIDView.as_view(), name='certificate_update'),
    path('certificate/<uuid:uuid>/delete/', views.CertificateDeleteByUUIDView.as_view(), name='certificate_delete'),
    path('certificates/', views.CertificateListView.as_view(), name='certificate_list'),

    # User-specific certificate views
    path('my-certificates/', views.UserCertificateListView.as_view(), name='my_certificates_list'),
    # Optional alias to accept a UUID param even if unused by the view (matches template usage)
    path('my-certificates/<uuid:uuid>/', views.UserCertificateListView.as_view(), name='my_certificates'),
    path('certificates/details/<int:pk>/', views.UserCertificateDetailView.as_view(), name='user_certificate_detail'),
    path('my-certificates/details/<uuid:uuid>/', views.UserCertificateDetailByUUIDView.as_view(), name='my_certificate_detail'),
    
    # Shared certificates view and management
    path('shared-certificates/', views.SharedCertificateListView.as_view(), name='shared_certificates_list'),

    # Public certificate view and PDF download
    path('certificate/public/<uuid:uuid>/', views.certificate_public_view, name='certificate_public_view'),
    path('certificate/public/<uuid:uuid>/pdf/', views.certificate_pdf_download, name='certificate_pdf_download'),
    path('certificate/toggle/<uuid:uuid>/', views.certificate_toggle_pending, name='certificate_toggle_pending'),
    path('certificate/claim/<uuid:uuid>/', views.claim_certificate, name='certificate_claim'),

    # In-person certificates routes removed; using ReportActivity via home app.

]
