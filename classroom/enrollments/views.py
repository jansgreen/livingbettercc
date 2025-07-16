# enrollments/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Enrollment
#from courses.models import Course
from django.urls import reverse
from django.contrib import messages

@login_required
def enrollment_list(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    return render(request, 'enrollments/enrollment_list.html', {'enrollments': enrollments})

@login_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
    return render(request, 'enrollments/enrollment_detail.html', {'enrollment': enrollment})

@login_required
def enrollment_create(request, course_id):
    Course = "test"
    course = get_object_or_404(Course, pk=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        messages.success(request, f"Te has inscrito en {course.title}.")
    else:
        messages.info(request, f"Ya estás inscrito en {course.title}.")
    return redirect('enrollments:enrollment-list')

@login_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, user=request.user)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, "Inscripción eliminada.")
        return redirect('enrollments:enrollment-list')
    return render(request, 'enrollments/enrollment_confirm_delete.html', {'enrollment': enrollment})

# Create your views here.
