from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from authentication.minerd.models import ReportAccountMinerd, Campo
from authentication.minerd.forms import ReportAccountMinerdForm
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)





# Create your views here.
def report_account_miner_create(request):
    report = ReportAccountMinerd()
    campos = Campo.objects.all()
    form = ReportAccountMinerdForm()
    if request.method == 'POST':
        form = ReportAccountMinerdForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.save()
            selected_campos_ids = request.POST.getlist('campos')
            for campo_id in selected_campos_ids:
                campo = get_object_or_404(Campo, id=campo_id)
                report.campos.add(campo)
            report.save()
            messages.success(request, 'Reporte creado exitosamente.')
            return redirect('minerd:report_account_miner_list')
        else:
            messages.error(request, f'Error al crear el reporte: {form.errors}')

    context = {
        'form': form,
        'report': report,
        'campos': campos,
    }
    return render(request, 'minerd/report_account_minerd_create.html', context)

def report_account_miner_list(request):
    reports = ReportAccountMinerd.objects.all()
    return render(request, 'minerd/report_account_minerd_list.html', {'reports': reports})

def report_account_miner_update(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    campos = Campo.objects.all()
    if request.method == 'POST':
        form = ReportAccountMinerdForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            selected_campos_ids = request.POST.getlist('campos')
            report.campos.clear()
            for campo_id in selected_campos_ids:
                campo = get_object_or_404(Campo, id=campo_id)
                report.campos.add(campo)
            report.save()
            messages.success(request, 'Reporte actualizado exitosamente.')
            return redirect('minerd:report_account_miner_list')
    else:
        form = ReportAccountMinerdForm(instance=report)
    context = {
        'form': form,
        'report': report,
        'campos': campos,
    }
    return render(request, 'minerd/report_account_minerd_update.html', context)

def report_account_miner_delete(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Reporte eliminado exitosamente.')
        return redirect('minerd:report_account_miner_list')
    return render(request, 'minerd/report_account_minerd_delete.html', {'report': report})

def report_account_miner_detail(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    return render(request, 'minerd/report_account_minerd_detail.html', {'report': report})


def report_account_miner_list(request):
    reports = ReportAccountMinerd.objects.all()
    return render(request, 'minerd/report_account_minerd_list.html', {'reports': reports})

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
    return render(request, 'minerd/report_account_minerd_update.html', {'report': report, 'campos': campos})

def report_account_miner_delete(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Reporte eliminado exitosamente.')
        return redirect('minerd:report_account_miner_list')
    return render(request, 'minerd/report_account_minerd_delete.html', {'report': report})

def report_account_miner_detail(request, pk):
    report = get_object_or_404(ReportAccountMinerd, pk=pk)
    return render(request, 'minerd/report_account_minerd_detail.html', {'report': report})

