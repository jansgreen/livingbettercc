from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course, Lesson, Material, Module
from .forms import CourseForm, ModuleForm, LessonForm, MaterialForm

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

def lesson_list(request):
    lessons = Lesson.objects.all()
    return render(request, 'classroom/lesson_list.html', {'lessons': lessons})

def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'classroom/lesson_detail.html', {'lesson': lesson})

def lesson_create(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lesson_list')
    else:
        form = LessonForm()
    return render(request, 'classroom/lesson_form.html', {'form': form})

def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('lesson_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'classroom/lesson_form.html', {'form': form})

def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        return redirect('lesson_list')
    return render(request, 'classroom/lesson_confirm_delete.html', {'lesson': lesson})

def material_list(request):
    materials = Material.objects.all()
    return render(request, 'classroom/material_list.html', {'materials': materials})

def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'classroom/material_detail.html', {'material': material})

def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('material_list')
    else:
        form = MaterialForm()
    return render(request, 'classroom/material_form.html', {'form': form})

def material_update(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            return redirect('material_list')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'classroom/material_form.html', {'form': form})

def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        return redirect('material_list')
    return render(request, 'classroom/material_confirm_delete.html', {'material': material})

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
    success_url = '/classroom/modules/'

class ModuleUpdateView(UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'classroom/module_form.html'
    success_url = '/modules/'

class ModuleDeleteView(DeleteView):
    model = Module
    template_name = 'classroom/module_confirm_delete.html'
    success_url = '/modules/'
