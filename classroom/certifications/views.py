from django.utils import timezone
from django.db.models import Count, Max, Sum, Q, F
from django.db.models.functions import Coalesce

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import InPersonCertificateIssueForm
from .models import Certificate, InPersonCategory, InPersonCertificateIssue
from classroom.courses.models import Course
from classroom.courses.services.taod_stats import get_taod_stats
from django.http import HttpResponse, FileResponse
from django.template.loader import get_template
import os


def get_inperson_stats_by_course():
    """
    Obtiene estadísticas de certificados presenciales agrupados por curso y año.
    Retorna una estructura optimizada para mostrar en templates.
    """
    issues = (
        InPersonCertificateIssue.objects
        .select_related("course")
        .order_by("-issued_date")
        .values("course", "issued_date__year")
        .annotate(
            course_title=F("course__title"),
            total_quantity=Sum("quantity"),
            total_presencial=Sum("in_person_total"),
            total_impact=Sum("impact"),
            count_issues=Count("id")
        )
    )
    
    # Agrupar por curso
    courses_stats = {}
    for issue in issues:
        course_id = issue["course"]
        course_title = issue["course_title"]
        year = issue["issued_date__year"]
        
        if course_id not in courses_stats:
            courses_stats[course_id] = {
                "title": course_title,
                "years": {},
                "total_quantity": 0,
                "total_presencial": 0,
                "total_impact": 0,
            }
        
        courses_stats[course_id]["years"][year] = {
            "quantity": issue["total_quantity"],
            "presencial": issue["total_presencial"],
            "impact": issue["total_impact"],
        }
        
        courses_stats[course_id]["total_quantity"] += issue["total_quantity"] or 0
        courses_stats[course_id]["total_presencial"] += issue["total_presencial"] or 0
        courses_stats[course_id]["total_impact"] += issue["total_impact"] or 0
    
    return courses_stats


@login_required
def listar_certificados(request):
    certificados = Certificate.objects.filter(user=request.user).select_related('course')
    total_certificates = Certificate.objects.count()
    # Preparar una lista de depuración con algunos campos clave para ayudar a diagnosticar coincidencias
    certificados = list(Certificate.objects.select_related('user', 'course').values('id', 'user__username', 'course__title', 'certificate_number', 'public_uuid'))
    context = {
        'certificados': certificados,
        'total_certificates': total_certificates,
    }
    return render(request, 'certifications/certificate_list.html', context)

def _can_manage_in_person(request) -> bool:
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return False
    return bool(user.is_superuser or user.is_staff or user.has_perm('groups.access_module'))

# Views para gestionar certificados presenciales (InPersonCertificateIssue)
@login_required
def inperson_list(request):

    issues = (
        InPersonCertificateIssue.objects
        .select_related("course", "created_by")
        .order_by("-issued_date", "course__title", "district")
    )

    total_issues = issues.count()
    total_presencial = issues.aggregate(t=Sum("in_person_total"))["t"] or 0
    total_impact = issues.aggregate(t=Sum("impact"))["t"] or 0

    context = {
        "issues": issues,
        "total_issues": total_issues,
        "total_presencial": total_presencial,
        "total_impact": total_impact,
    }

    return render(request, "certifications/inperson_list.html", context)


@login_required
def inperson_create(request):
    if not _can_manage_in_person(request):
        return render(request, 'dashboard/dashboard_base.html', {'error': 'No autorizado'})

    initial = {}
    course_id = request.GET.get('course')
    if course_id:
        try:
            initial['course'] = int(course_id)
        except Exception:
            pass

    if request.method == 'POST':
        form = InPersonCertificateIssueForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'Registro presencial guardado.')
            return redirect('certifications:inperson_list')
        messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = InPersonCertificateIssueForm(initial=initial)

    return render(request, 'certifications/inperson_form.html', {
        'form': form,
        'mode': 'create',
    })

@login_required
def inperson_update(request, pk):
    if not _can_manage_in_person(request):
        return render(request, 'dashboard/dashboard_base.html', {'error': 'No autorizado'})

    obj = get_object_or_404(InPersonCertificateIssue, pk=pk)
    if request.method == 'POST':
        form = InPersonCertificateIssueForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro presencial actualizado.')
            return redirect('certifications:inperson_list')
        messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = InPersonCertificateIssueForm(instance=obj)

    return render(request, 'certifications/inperson_form.html', {
        'form': form,
        'mode': 'edit',
        'object': obj,
    })

@login_required
def inperson_delete(request, pk):
    if not _can_manage_in_person(request):
        return render(request, 'dashboard/dashboard_base.html', {'error': 'No autorizado'})

    obj = get_object_or_404(InPersonCertificateIssue, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Registro presencial eliminado.')
        return redirect('certifications:inperson_list')

    return render(request, 'certifications/inperson_confirm_delete.html', {
        'object': obj,
    })

@login_required
def create_certificate_for_user(user, course):
    cert = Certificate.objects.filter(user=user, course=course).first()
    if not cert:
        cert = Certificate.objects.create(
            user=user,
            course=course,
            certificate_number=f"CERT-{user.id}-{course.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            issued_date=timezone.now().date(),
        )
    return cert

def certificate_public_view(request, uuid):
    certificate = get_object_or_404(Certificate, public_uuid=uuid)
    context = {
        'certificate': certificate,
        'user': certificate.user,
        'course': certificate.course,
        'date': certificate.issued_date,
    }
    return render(request, 'public_certificate.html', context)

@login_required
def certificate_pdf_download(request, uuid):
    certificate = get_object_or_404(Certificate, public_uuid=uuid)

    # If a PDF file exists, serve it directly
    if certificate.pdf_file and certificate.pdf_file.name:
        try:
            file_path = certificate.pdf_file.path
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        except Exception:
            pass

    # Render HTML certificate template with background image and user data
    template = get_template('certifications/certificate_template.html')
    html = template.render({
        'user': certificate.user,
        'course': certificate.course,
        'date': certificate.issued_date,
    })

    # Serve HTML for download only (no PDF generation)
    response = HttpResponse(html, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="certificado_{certificate.user.username}.html"'
    return response


class _StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return bool(getattr(self.request, "user", None) and self.request.user.is_staff)


class InPersonCategoryListView(_StaffRequiredMixin, ListView):
    model = InPersonCategory
    template_name = "certifications/inperson_category_list.html"
    context_object_name = "categories"
    paginate_by = 50

    def get_queryset(self):
        return InPersonCategory.objects.order_by("name")


class InPersonCategoryCreateView(_StaffRequiredMixin, CreateView):
    model = InPersonCategory
    fields = ["name", "description"]
    template_name = "certifications/inperson_category_form.html"
    success_url = reverse_lazy("certifications:inperson_category_list")


class InPersonCategoryUpdateView(_StaffRequiredMixin, UpdateView):
    model = InPersonCategory
    fields = ["name", "description"]
    template_name = "certifications/inperson_category_form.html"
    success_url = reverse_lazy("certifications:inperson_category_list")


class InPersonCategoryDeleteView(_StaffRequiredMixin, DeleteView):
    model = InPersonCategory
    template_name = "certifications/inperson_category_confirm_delete.html"
    success_url = reverse_lazy("certifications:inperson_category_list")
