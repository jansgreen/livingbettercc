from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from authentication.models import Profiles, Students, Address
from authentication.minerd.models import ReportAccountMinerd, Campo
from authentication.forms import ProfileForm, AddressForm
from .forms import studentRegisterForm, StudentByDistrictForm
from authentication.forms import BootstrapUserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group
from .exequatur import exequatur_consurt
from django.contrib.auth.models import User
import logging
from classroom.enrollments.models import Enrollment
from classroom.courses.models import Course, Module, Lesson

logger = logging.getLogger(__name__)





# Create your views here.
def report_account_miner_create(request):
    report = ReportAccountMinerd()
    campos = Campo.objects.all()
    if request.method == 'POST':
        report.titulo = request.POST.get('titulo')
        report.centro_educativo = request.POST.get('centro_educativo')
        report.regional = request.POST.get('regional')
        report.responsabilidades = request.POST.get('responsabilidades')
        report.temas_impartidos = request.POST.get('temas_impartidos')
        report.fecha = request.POST.get('fecha')
        report.save()
        
        selected_campos_ids = request.POST.getlist('campos')
        for campo_id in selected_campos_ids:
            campo = get_object_or_404(Campo, id=campo_id)
            report.campos.add(campo)
        
        report.save()
        messages.success(request, 'Reporte creado exitosamente.')
        return redirect('report_account_miner_list')
    return render (request, 'report_account_minerd.html', {'report': report, 'campos': campos})

def report_account_miner_list(request):
    reports = ReportAccountMinerd.objects.all()
    return render(request, 'report_account_minerd_list.html', {'reports': reports})

def report_account_miner_update(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    campos = Campo.objects.all()
    if request.method == 'POST':
        report.titulo = request.POST.get('titulo')
        report.centro_educativo = request.POST.get('centro_educativo')
        report.regional = request.POST.get('regional')
        report.responsabilidades = request.POST.get('responsabilidades')
        report.temas_impartidos = request.POST.get('temas_impartidos')
        report.fecha = request.POST.get('fecha')
        report.save()
        
        selected_campos_ids = request.POST.getlist('campos')
        report.campos.clear()
        for campo_id in selected_campos_ids:
            campo = get_object_or_404(Campo, id=campo_id)
            report.campos.add(campo)
        
        report.save()
        messages.success(request, 'Reporte actualizado exitosamente.')
        return redirect('report_account_miner_list')
    return render(request, 'report_account_minerd.html', {'report': report, 'campos': campos})

def report_account_miner_delete(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Reporte eliminado exitosamente.')
        return redirect('report_account_miner_list')
    return render(request, 'report_account_minerd_confirm_delete.html', {'report': report})

def report_account_miner_detail(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    return render(request, 'report_account_minerd_detail.html', {'report': report})

