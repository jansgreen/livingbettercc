from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Lesson, Material, Module
from .forms import CourseForm, ModuleForm

def curso_principal(request, curso_id):
    curso = get_object_or_404(Course, id=curso_id)
    modulos = Course.modules.all()
    return render(request, 'classroom/curso_principal.html', {'curso': curso, 'modulos': modulos})

def leccion_detalle(request, leccion_id):
    leccion = get_object_or_404(Lesson, id=leccion_id)
    materiales = leccion.materials.all()
    return render(request, 'classroom/leccion_detalle.html', {'leccion': leccion, 'materiales': materiales})

def admin_panel(request):
    cursos = Course.objects.all()
    return render(request, 'classroom/admin_panel.html', {'cursos': cursos})

def curso_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        form = CourseForm()
    return render(request, 'classroom/course_form.html', {'form': form})

def curso_update(request, curso_id):
    curso = get_object_or_404(Course, id=curso_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect('admin_panel')
    else:
        form = CourseForm(instance=curso)
    return render(request, 'classroom/course_form.html', {'form': form})

def curso_delete(request, curso_id):
    curso = get_object_or_404(Course, id=curso_id)
    if request.method == 'POST':
        curso.delete()
        return redirect('admin_panel')
    return render(request, 'classroom/curso_confirm_delete.html', {'curso': curso})

def curso_list(request):
    cursos = Course.objects.all()
    return render(request, 'classroom/course_list.html', {'cursos': cursos})

class ModuleListView(ListView):
    model = Module
    template_name = 'classroom/module_list.html'

class ModuleDetailView(DetailView):
    model = Module
    template_name = 'classroom/module_detail.html'

class ModuleCreateView(CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'classroom/module_form.html'
    success_url = '/modules/'

class ModuleUpdateView(UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'classroom/module_form.html'
    success_url = '/modules/'

class ModuleDeleteView(DeleteView):
    model = Module
    template_name = 'classroom/module_confirm_delete.html'
    success_url = '/modules/'
