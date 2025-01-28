from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required



@login_required
def evidence_google(request):
    return render(request, 'evidence.html')