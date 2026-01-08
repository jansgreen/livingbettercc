from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from authentication.models import Profiles, Students
from authentication.address.forms import AddressForm
from authentication.forms import ProfileForm
from .forms import StudentByDistrictForm
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
    return render(request, 'student_form.html', {'form': form})

def student_create_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user.is_staff = False  # Ensure the user is not a staff member
            profile.user.save()
            profile.save()
            request.user.groups.add(name='students')
            
            return redirect('course_list')  # Redirect to student list after creation
    else:
        form = ProfileForm()
    return render(request, 'student_create.html', {'form': form})

def student_update_view(request, pk):
    student = get_object_or_404(Profiles, pk=pk, user__is_staff=False)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = ProfileForm(instance=student)
    return render(request, 'student_update.html', {'form': form})

def student_delete_view(request, pk):
    student = get_object_or_404(Profiles, pk=pk, user__is_staff=False)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'student_confirm_delete.html', {'student': student})

# tengo que crear la funcion Ver mi perfil de estudiante
def student_my_info(request, pk):
    student = Students.objects.get(pk=pk)
    context = {
        'student': student
    }
    return render(request, 'my_student.html', context)

def student_list_view(request):
    students = Students.objects.all()
    context = {
        'students': students
    }
    return render(request, 'student_list.html', context)

def student_detail_view(request, pk):
    student = Students.objects.get(pk=pk)
    context = {
        'student': student,

    }
       
    return render(request, 'student_detail.html', context)    

def student_by_district(request):
    form = StudentByDistrictForm(request.POST)
    if request.method == 'POST':
        form = StudentByDistrictForm(request.POST)
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
            student.save()
            messages.success(request, 'Ya casi falta poco.')
            addr_url = reverse('authentication:address:address_create', kwargs={'address_type': 'laboral', 'pk': request.user.id})
            next_url = reverse('courses:my_course')
            return redirect(f"{addr_url}?next={next_url}")
        else:
            messages.error(request, f'Por favor corrija los siguientes errores: {form.errors}')
            return render(request, "by_district_form.html", {'form': form})

    return render(request, "by_district_form.html", {'form': form})
