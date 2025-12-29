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
from django.contrib import messages
from django.forms import inlineformset_factory
from django.forms import NumberInput, TextInput


# Import app models used for dashboard counts
from authentication.models.students import Students
from authentication.formbuilder.models import FormDefinition
from classroom.courses.models import Course
from classroom.courses.models import CourseYearStat
from classroom.courses.models import Program
from classroom.courses.services.taod_stats import get_taod_stats
from classroom.certifications.models import Certificate, InPersonCertificateIssue
from authentication.models.customers import Customers
from django.db.models import Case, Count, F, IntegerField, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from classroom.certifications.views import get_inperson_stats_by_course


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

    courses_stats = (
        Course.objects.all()
        .annotate(
            auto_certified_count=Count('certificates', distinct=True),
            manual_year_certified_add=Coalesce(Sum('year_stats__manual_certified_add'), 0),
            total_certified_count=(
                Coalesce(F('manual_certified_add'), 0)
                + Coalesce(Sum('year_stats__manual_certified_add'), 0)
                + Count('certificates', distinct=True)
            ),
        )
        .order_by('-published', 'title')
    )
    context = {
        'students_count': students_count,
        'users_count': users_count,
        'forms_count': forms_count,
        'courses_count': courses_count,
        'customers_count': customers_count,
        'beca_applications_count': beca_applications_count,
        'becados_count': becados_count,
        'is_student': ('student' in user_groups) or ('students' in user_groups),
        'is_tecnico': 'tecnico' in user_groups,
        'is_facilitador': 'facilitador' in user_groups,
        'courses_stats': courses_stats,
        'inperson_stats': get_inperson_stats_by_course(),
    }

    taod = get_taod_stats(top_n=10)
    context['taod_kpis'] = taod.taod_kpis
    context['taod_years'] = taod.taod_years
    context['top_courses'] = taod.top_courses

    taod_program = Program.objects.filter(name='TAOD').first()
    if taod_program:
        year_sum_sq = (
            CourseYearStat.objects.filter(course=OuterRef('pk'))
            .values('course')
            .annotate(total=Coalesce(Sum('manual_certified_add'), 0))
            .values('total')[:1]
        )
        in_person_sq = (
            InPersonCertificateIssue.objects.filter(course=OuterRef('pk'))
            .values('course')
            .annotate(total=Coalesce(Sum('quantity'), 0))
            .values('total')[:1]
        )
        cert_count_sq = (
            Certificate.objects.filter(course=OuterRef('pk'))
            .values('course')
            .annotate(total=Count('id'))
            .values('total')[:1]
        )

        taod_courses = (
            Course.objects.filter(program=taod_program)
            .annotate(
                manual_year_certified_add=Coalesce(Subquery(year_sum_sq, output_field=IntegerField()), Value(0)),
                in_person_issued_sum=Coalesce(Subquery(in_person_sq, output_field=IntegerField()), Value(0)),
                auto_certified_count=Coalesce(Subquery(cert_count_sq, output_field=IntegerField()), Value(0)),
            )
            .annotate(
                in_person_total=Case(
                    When(in_person_issued_sum__gt=0, then=F('in_person_issued_sum')),
                    default=(Coalesce(F('manual_certified_add'), 0) + Coalesce(F('manual_year_certified_add'), 0)),
                    output_field=IntegerField(),
                ),
                total_certified_count=(Coalesce(F('auto_certified_count'), 0) + F('in_person_total')),
            )
            .order_by('-total_certified_count', 'title')
        )
    else:
        taod_courses = Course.objects.none()

    context['taod_courses'] = taod_courses
    return render(request, 'dashboard.html', context)


def course_year_stats_edit(request, pk):
    if not request.user.is_staff:
        return render(request, 'dashboard/dashboard_base.html', {'error': 'No autorizado'})

    course = get_object_or_404(Course, pk=pk)

    CourseYearStatFormSet = inlineformset_factory(
        Course,
        CourseYearStat,
        fields=('year', 'manual_certified_add', 'note'),
        widgets={
            'year': NumberInput(attrs={'class': 'form-control'}),
            'manual_certified_add': NumberInput(attrs={'class': 'form-control'}),
            'note': TextInput(attrs={'class': 'form-control'}),
        },
        extra=1,
        can_delete=True,
    )

    if request.method == 'POST':
        formset = CourseYearStatFormSet(request.POST, instance=course)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Certificaciones por año actualizadas.')
            return redirect('dashboard')
        messages.error(request, 'Revisa los errores del formulario.')
    else:
        formset = CourseYearStatFormSet(instance=course, queryset=course.year_stats.order_by('-year'))

    return render(request, 'dashboard/course_year_stats.html', {
        'course': course,
        'formset': formset,
    })
