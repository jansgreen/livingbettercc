from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def beca_application_action(request, app_id):
    if not request.user.is_staff or request.method != 'POST':
        return redirect('beca_applications_list')
    from classroom.enrollments.models import BecaApplication
    app = get_object_or_404(BecaApplication, id=app_id)
    action = request.POST.get('action')
    if action == 'aprobar':
        app.estado = 'aprobada'
        app.save()
    elif action == 'rechazar':
        app.estado = 'rechazada'
        app.save()
    return redirect('beca_applications_list')
from classroom.enrollments.models import BecaApplication

def beca_applications_list(request):
    # Solo staff puede ver
    if not request.user.is_staff:
        return render(request, 'dashboard/dashboard_base.html', {'error': 'No autorizado'})
    estado = request.GET.get('estado', 'todos')
    qs = BecaApplication.objects.select_related('user', 'course', 'address').order_by('-fecha_aplicacion')
    if estado != 'todos':
        qs = qs.filter(estado=estado)
    return render(request, 'dashboard/beca_applications_list.html', {
        'beca_applications': qs,
        'estado': estado,
    })
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

    from classroom.enrollments.models import BecaApplication
    beca_applications_count = BecaApplication.objects.count()
    becados_count = BecaApplication.objects.filter(estado='aprobada').count()
    # Group checks for template logic
    user_groups = request.user.groups.values_list('name', flat=True) if request.user.is_authenticated else []
    context = {
        'students_count': students_count,
        'users_count': users_count,
        'forms_count': forms_count,
        'courses_count': courses_count,
        'customers_count': customers_count,
        'beca_applications_count': beca_applications_count,
        'becados_count': becados_count,
        'is_student': 'student' in user_groups,
        'is_tecnico': 'tecnico' in user_groups,
        'is_facilitador': 'facilitador' in user_groups,
    }
    return render(request, 'dashboard.html', context)
