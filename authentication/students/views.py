from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from authentication.models import Profiles, Students
from authentication.address.forms import AddressForm
from authentication.forms import ProfileForm
from .forms import StudentByDistrictForm
from authentication.forms import BootstrapUserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Count, Q
from .exequatur import exequatur_consurt
from django.contrib.auth.models import User
import logging
from classroom.enrollments.models import Enrollment
from classroom.courses.models import Course, Module, Lesson

logger = logging.getLogger(__name__)

STUDENT_GROUP_ALIASES = (
    "student",
    "students",
    "estudiante",
    "estudiantes",
    "estudiante_becado",
    "estudiantes_becados",
)



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
            group, _ = Group.objects.get_or_create(name='estudiantes')
            request.user.groups.add(group)
            
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
    group_query = Q()
    for group_name in STUDENT_GROUP_ALIASES:
        group_query |= Q(groups__name__iexact=group_name)

    users = (
        User.objects
        .filter(group_query | Q(students__isnull=False) | Q(scholarship_info__isnull=False))
        .select_related('profiles', 'students', 'scholarship_info')
        .prefetch_related('groups')
        .annotate(certificates_count=Count('certificates', distinct=True))
        .distinct()
        .order_by('first_name', 'last_name', 'username')
    )

    students = []
    for user in users:
        profile = getattr(user, 'profiles', None)
        student_record = getattr(user, 'students', None)
        scholarship_info = getattr(user, 'scholarship_info', None)
        group_names = {name.lower() for name in user.groups.values_list('name', flat=True)}
        is_scholarship = bool(
            scholarship_info
            or group_names.intersection({'estudiante_becado', 'estudiantes_becados'})
        )

        students.append({
            'user': user,
            'first_name': user.first_name or user.username,
            'last_name': user.last_name or '',
            'email': user.email or 'Sin correo',
            'student_type': 'Becado' if is_scholarship else 'Regular',
            'regional': getattr(scholarship_info, 'regional', None) or getattr(student_record, 'regional', '') or 'No registrada',
            'district': getattr(scholarship_info, 'district', None) or getattr(student_record, 'distrito_educativo', '') or 'No registrado',
            'province': getattr(scholarship_info, 'province', None) or 'No registrada',
            'country': scholarship_info.get_country_display() if scholarship_info else 'No registrado',
            'certificates_count': user.certificates_count,
            'academic_level': profile.get_nivel_academico_display() if profile and profile.nivel_academico else 'No registrado',
            'profession': getattr(profile, 'profesion', '') or 'No registrada',
        })

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
