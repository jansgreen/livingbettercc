from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from authentication.models import Profiles, Students, Address
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

def student_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user.is_staff = False  # Ensure the user is not a staff member
            profile.user.save()
            profile.save()
            return redirect('student_list')  # Redirect to student list after creation
    else:
        form = ProfileForm()
    return render(request, 'students/student_form.html', {'form': form})

def student_create_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user.is_staff = False  # Ensure the user is not a staff member
            profile.user.save()
            profile.save()
            return redirect('student_list')  # Redirect to student list after creation
    else:
        form = ProfileForm()
    return render(request, 'students/student_create.html', {'form': form})

def student_update_view(request, pk):
    student = get_object_or_404(Profiles, pk=pk, user__is_staff=False)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = ProfileForm(instance=student)
    return render(request, 'students/student_update.html', {'form': form})

def student_delete_view(request, pk):
    student = get_object_or_404(Profiles, pk=pk, user__is_staff=False)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})

def student_district_view(request, pk):
    
    if request.method == 'POST':
        form = BootstrapUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='students')
            user.groups.add(group)
            messages.success(request, 'Estudiante registrado exitosamente.')
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = BootstrapUserCreationForm()
    return render(request, 'students/student_district.html', {'form': form})

# Student registration view
def student_register_view(request):
    group, _ = Group.objects.get_or_create(name='students')

    # Si ya está autenticado, redirígelo según su situación
    if request.user.is_authenticated:
        if Students.objects.filter(user=request.user).exists():
            student = Students.objects.get(user=request.user)
            if Address.objects.filter(user=student.user).exists():
                return redirect('students:student_list')
            else:
                return redirect('address_create', address_type='laboral')
        else:
            return redirect('students:student_by_district')

    # Si no está autenticado, mostramos el formulario
    form = studentRegisterForm()
    if request.method == 'POST':
        form = studentRegisterForm(request.POST)
        if form.is_valid():
            check = request.POST.get('Check')
            user = form.save(commit=False)
            user.save()  # Ahora ya tiene ID
            user.groups.add(group)

            messages.success(request, 'Estudiante registrado exitosamente.')

            if check:
                return redirect('students:student_by_district')
            return redirect('students:student_by_district')
        else:
            messages.error(request, f'{form.errors} Error al registrar estudiante. Por favor, corrige los errores.')

    return render(request, 'students/students_register.html', {'form': form})

def student_by_district(request):
    student_instance, created = Students.objects.get_or_create(user=request.user)
    form = StudentByDistrictForm(request.POST or None, instance=student_instance)
    if request.method == 'POST':
        form = StudentByDistrictForm(request.POST, instance=request.user)
        if form.is_valid():
            student, created = Students.objects.get_or_create(
                user=request.user,
                defaults=form.cleaned_data
            )
            if not created:
                # Ya existía el estudiante, puedes actualizarlo si quieres
                for key, value in form.cleaned_data.items():
                    setattr(student, key, value)
                student.save()
            # Asignar el grupo de estudiantes
            group, _ = Group.objects.get_or_create(name='students')
            student.user.groups.add(group)

            student.save()
            messages.success(request, 'Ya casi falta poco.')
            return redirect('address_create', address_type='laboral')
        else:
            messages.error(request, f'Por favor corrija los siguientes errores: {form.errors}')
            return render(request, "students/by_district.html", {'form': form})

    return render(request, "students/by_district.html", {'form': form})
