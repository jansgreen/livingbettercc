from django.urls import path
from . import views

urlpatterns = [
    path('evidences/evidence_google/', views.evidence_google, name='evidence_google'),
]
