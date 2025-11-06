from django.shortcuts import render
from django.contrib.auth.models import User


# Import app models used for dashboard counts
from authentication.models.students import Students
from authentication.formbuilder.models import FormDefinition
from classroom.courses.models import Course
from authentication.models.customers import Customers


def dashboards(request):
    """Render the dashboard overview with counts for key resources.

    Context variables provided to the template:
    - students_count
    - users_count
    - forms_count
    - courses_count
    - customers_count
    """
    students_count = Students.objects.count()
    users_count = User.objects.count()
    forms_count = FormDefinition.objects.count()
    courses_count = Course.objects.count()
    customers_count = Customers.objects.count()

    context = {
        'students_count': students_count,
        'users_count': users_count,
        'forms_count': forms_count,
        'courses_count': courses_count,
        'customers_count': customers_count,
    }

    return render(request, 'dashboard.html', context)
