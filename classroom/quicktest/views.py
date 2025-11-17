from django.shortcuts import render, get_object_or_404, redirect
from .models import QuickTest
from classroom.courses.models import Module
from django.contrib.auth.decorators import login_required

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
