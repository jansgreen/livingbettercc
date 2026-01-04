# urls.py
from django.urls import path
from . import views

app_name = 'certifications'

urlpatterns = [
    path('list/', views.listar_certificados, name='certificate_list'),
    path('certificate/<uuid:uuid>/', views.certificate_public_view, name='certificate_public_view'),
    path('certificate/<uuid:uuid>/download/', views.certificate_pdf_download, name='certificate_pdf_download'),

    # Presenciales (manual por distrito)
    path('in-person/', views.inperson_list, name='inperson_list'),
    path('in-person/new/', views.inperson_create, name='inperson_create'),
    path('in-person/<int:pk>/edit/', views.inperson_update, name='inperson_update'),
    path('in-person/<int:pk>/delete/', views.inperson_delete, name='inperson_delete'),

    # In-person categories
    path("inperson/categories/", views.InPersonCategoryListView.as_view(), name="inperson_category_list"),
    path("inperson/categories/create/", views.InPersonCategoryCreateView.as_view(), name="inperson_category_create"),
    path("inperson/categories/<int:pk>/update/", views.InPersonCategoryUpdateView.as_view(), name="inperson_category_update"),
    path("inperson/categories/<int:pk>/delete/", views.InPersonCategoryDeleteView.as_view(), name="inperson_category_delete"),
]
