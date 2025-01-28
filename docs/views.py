from django.shortcuts import render, redirect
from .forms import ImplementationEvidenceForm
from django.contrib.auth.decorators import login_required
from .models import ImplementationEvidence



@login_required
def evidence_google(request):
    return render(request, 'evidence.html')