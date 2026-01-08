from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from classroom.courses.models import Module
from .models import QuickTest, QuickTestDefinition, QuickTestQuestion
from .forms import QuickTestDefinitionForm, QuickTestQuestionForm

@login_required
def quicktest_list(request):
    tests = QuickTest.objects.filter(user=request.user)
    return render(request, 'quicktest/quicktest_list.html', {'tests': tests})

@login_required
def quicktest_detail(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    return render(request, 'quicktest/quicktest_detail.html', {'test': test})

@login_required
def quicktest_create(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        score = request.POST.get('score')
        QuickTest.objects.create(module=module, user=request.user, score=score)
        return redirect('quicktest_list')
    return render(request, 'quicktest/quicktest_form.html', {'module': module})

@login_required
def quicktest_update(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    if request.method == 'POST':
        score = request.POST.get('score')
        test.score = score
        test.save()
        return redirect('quicktest_detail', pk=test.pk)
    return render(request, 'quicktest/quicktest_form.html', {'test': test})

@login_required
def quicktest_delete(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    if request.method == 'POST':
        test.delete()
        return redirect('quicktest_list')
    return render(request, 'quicktest/quicktest_confirm_delete.html', {'test': test})


# --------------------------
# Staff CRUD for QuickTests
# --------------------------

def _ensure_staff(request):
    if not request.user.is_authenticated:
        return False
    return request.user.is_staff or request.user.is_superuser


@login_required
def qdef_list(request):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    defs = QuickTestDefinition.objects.select_related('module', 'module__course').order_by('module__course__title', 'module__order')
    return render(request, 'quicktest/qdef_list.html', {'definitions': defs})


@login_required
def qdef_create(request):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    if request.method == 'POST':
        form = QuickTestDefinitionForm(request.POST)
        if form.is_valid():
            qdef = form.save()
            messages.success(request, 'QuickTest creado.')
            return redirect('quicktest:qdef_list')
    else:
        form = QuickTestDefinitionForm()
    return render(request, 'quicktest/qdef_form.html', {'form': form})


@login_required
def qdef_update(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=pk)
    if request.method == 'POST':
        form = QuickTestDefinitionForm(request.POST, instance=qdef)
        if form.is_valid():
            form.save()
            messages.success(request, 'QuickTest actualizado.')
            return redirect('quicktest:qdef_list')
    else:
        form = QuickTestDefinitionForm(instance=qdef)
    return render(request, 'quicktest/qdef_form.html', {'form': form, 'qdef': qdef})


@login_required
def qdef_delete(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=pk)
    if request.method == 'POST':
        qdef.delete()
        messages.success(request, 'QuickTest eliminado.')
        return redirect('quicktest:qdef_list')
    return render(request, 'quicktest/qdef_confirm_delete.html', {'qdef': qdef})


@login_required
def q_list(request, def_id):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    qs = qdef.questions.all()
    return render(request, 'quicktest/q_list.html', {'qdef': qdef, 'questions': qs})


@login_required
def q_create(request, def_id):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    if request.method == 'POST':
        form = QuickTestQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.definition = qdef
            q.save()
            messages.success(request, 'Pregunta creada.')
            return redirect('quicktest:q_list', def_id=qdef.id)
    else:
        form = QuickTestQuestionForm()
    return render(request, 'quicktest/q_form.html', {'form': form, 'qdef': qdef})


@login_required
def q_update(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    q = get_object_or_404(QuickTestQuestion, pk=pk)
    if request.method == 'POST':
        form = QuickTestQuestionForm(request.POST, instance=q)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pregunta actualizada.')
            return redirect('quicktest:q_list', def_id=q.definition_id)
    else:
        form = QuickTestQuestionForm(instance=q)
    return render(request, 'quicktest/q_form.html', {'form': form, 'qdef': q.definition, 'question': q})


@login_required
def q_delete(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    q = get_object_or_404(QuickTestQuestion, pk=pk)
    if request.method == 'POST':
        def_id = q.definition_id
        q.delete()
        messages.success(request, 'Pregunta eliminada.')
        return redirect('quicktest:q_list', def_id=def_id)
    return render(request, 'quicktest/q_confirm_delete.html', {'question': q})

