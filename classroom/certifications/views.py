from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.http import Http404
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.decorators.http import require_POST
from core.group_utils import has_group

from .models import Certificate, BecadoCertificateRequest, OnlineCertificateReport
from .forms import CertificateForm, BecadoCertificateRequestForm, OnlineCertificateReportForm
from .utils import get_online_certificates_by_course_year
from authentication.models.profiles import Profiles
from authentication.models.students import Students


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class CertificateCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = "certifications/certificate_form.html"
    success_url = reverse_lazy("certifications:certificate_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "create"
        ctx["certificate"] = None
        return ctx


class CertificateUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Certificate
    form_class = CertificateForm
    template_name = "certifications/certificate_form.html"
    success_url = reverse_lazy("certifications:certificate_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "update"
        ctx["certificate"] = self.object
        return ctx


class CertificateDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Certificate
    template_name = "certifications/certificate_confirm_delete.html"
    success_url = reverse_lazy("certifications:certificate_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["certificate"] = self.object
        return ctx


class CertificateListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Certificate
    template_name = "certifications/user_certificate_list.html"
    context_object_name = "certificados"

    def get_queryset(self):
        return Certificate.objects.select_related("user", "course").order_by("-issued_date")


class UserCertificateListView(LoginRequiredMixin, ListView):
    model = Certificate
    template_name = "certifications/my_certificates.html"
    context_object_name = "certificates"

    def get_queryset(self):
        return (
            Certificate.objects
            .select_related("course")
            .prefetch_related("becado_request")
            .filter(user=self.request.user)
            .order_by("-issued_date")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_becado"] = has_group(self.request.user, "estudiantes_becados")
        return ctx


class UserCertificateDetailView(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = "certifications/certificate.html"
    context_object_name = "certificate"

    # Si tu URL usa uuid: path("my/<uuid:uuid>/", UserCertificateDetailView.as_view(), ...)
    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uuid")
        pk = self.kwargs.get("pk")
        queryset = Certificate.objects.select_related("user", "course")
        if uuid:
            cert = get_object_or_404(queryset, uuid=uuid, user=self.request.user)
        else:
            cert = get_object_or_404(queryset, pk=pk, user=self.request.user)
        if cert.pending and not self.request.user.is_staff:
            raise Http404("No encontrado")
        return cert

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Alias para que el template funcione si usas "certificado"
        ctx["certificado"] = ctx["certificate"]

        # Datos extra útiles para el certificado (opcionales)
        user = ctx["certificate"].user
        ctx["student_name"] = (user.get_full_name() or user.username).strip()
        ctx["course_title"] = ctx["certificate"].course.title
        ctx.update(_certificate_template_context(ctx["certificate"]))
        return ctx

class SharedCertificateListView(LoginRequiredMixin, ListView):
    model = Certificate
    template_name = "certifications/user_certificate_list.html"
    context_object_name = "certificados"

    def get_queryset(self):
        # Placeholder: without an explicit 'shared' flag, reuse global list
        return Certificate.objects.select_related("user", "course").order_by("-issued_date")

# ---- Helpers / Public Views ----
def create_certificate_for_user(user, course):
    """Create or get a certificate for a (user, course) pair, idempotent.
    Becados remain pending until staff approval.
    """
    is_becado = has_group(user, "estudiantes_becados")
    with transaction.atomic():
        try:
            cert, _created = Certificate.objects.get_or_create(
                user=user,
                course=course,
                defaults={
                    "issued_date": timezone.now().date(),
                    "pending": bool(is_becado),
                },
            )
        except IntegrityError:
            cert = Certificate.objects.get(user=user, course=course)

    # If user is not becado, ensure certificate is active.
    if not is_becado and cert.pending:
        cert.pending = False
        cert.save(update_fields=["pending"])
    return cert

def _certificate_template_context(cert):
    student_name = (cert.user.get_full_name() or cert.user.username).strip()
    scholarship_info = getattr(cert.user, "scholarship_info", None)
    cert_location_text = ""
    cert_program_location_text = ""
    if scholarship_info and scholarship_info.is_complete():
        cert_program_location_text = (
            f"Regional {scholarship_info.regional}, "
            f"Distrito {scholarship_info.district}"
        )
        cert_location_text = (
            f"para la Regional {scholarship_info.regional}, "
            f"Distrito {scholarship_info.district}, "
            f"{scholarship_info.province}, "
            f"{scholarship_info.get_country_display()}"
        )
    return {
        "certificate": cert,
        "certificado": cert,
        "user": cert.user,
        "student_name": student_name,
        "course": cert.course,
        "course_title": cert.course.title,
        "issue_date": cert.issued_date,
        "cert_no": cert.cert_no,
        "cert_left_ref": getattr(settings, "CERT_LEFT_REF", None),
        "cert_right_ref": getattr(settings, "CERT_RIGHT_REF", None),
        "cert_brand": getattr(settings, "CERT_BRAND", None),
        "cert_implementer": getattr(settings, "CERT_IMPLEMENTER", None),
        "cert_sig1_name": getattr(settings, "CERT_SIG1_NAME", None),
        "cert_sig1_role": getattr(settings, "CERT_SIG1_ROLE", None),
        "cert_sig2_name": getattr(settings, "CERT_SIG2_NAME", None),
        "cert_sig2_role": getattr(settings, "CERT_SIG2_ROLE", None),
        "cert_quote": getattr(settings, "CERT_QUOTE", None),
        "cert_location_text": cert_location_text,
        "cert_program_location_text": cert_program_location_text,
    }

def certificate_public_view(request, uuid):
    cert = get_object_or_404(Certificate.objects.select_related("user", "course"), public_uuid=uuid)
    if cert.pending and not (request.user.is_authenticated and request.user.is_staff):
        raise Http404("No encontrado")
    ctx = _certificate_template_context(cert)
    return render(request, "certifications/certificate.html", ctx)

def certificate_toggle_pending(request, uuid):
    if not (request.user.is_authenticated and request.user.is_staff):
        raise Http404("No encontrado")
    cert = get_object_or_404(Certificate, uuid=uuid)
    cert.pending = not cert.pending
    cert.save(update_fields=["pending"])
    ctx = _certificate_template_context(cert)
    return render(request, "certifications/certificate.html", ctx)

def claim_certificate(request, uuid):
    if not request.user.is_authenticated:
        raise Http404("No encontrado")
    cert = get_object_or_404(Certificate, uuid=uuid, user=request.user)
    if not cert.pending:
        return redirect("certifications:my_certificates_list")

    if not has_group(request.user, "estudiantes_becados"):
        raise Http404("No encontrado")

    profile = Profiles.objects.filter(user=request.user).first()
    student = Students.objects.filter(user=request.user).first()
    telefono = ""
    if profile and getattr(profile, "telefono", None):
        telefono = profile.telefono
    elif student and getattr(student, "telefono", None):
        telefono = student.telefono

    initial = {
        "full_name": (request.user.get_full_name() or request.user.username).strip(),
        "email": request.user.email or "",
        "phone": telefono or "",
    }

    existing_request = getattr(cert, "becado_request", None)
    if request.method == "POST":
        form = BecadoCertificateRequestForm(request.POST, instance=existing_request)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.certificate = cert
            claim.user = request.user
            claim.course = cert.course
            claim.status = BecadoCertificateRequest.Status.PENDING
            claim.sent_at = timezone.now()
            claim.authorized_at = None
            claim.authorized_by = None
            claim.save()

            body = (
                "Solicitud de certificación (estudiante becado)\n\n"
                f"Nombre: {claim.full_name}\n"
                f"Centro educativo: {claim.educational_center}\n"
                f"Regional: {claim.regional}\n"
                f"Correo: {claim.email}\n"
                f"Teléfono: {claim.phone}\n"
                f"Curso: {cert.course.title}\n"
                f"Usuario: {request.user.username}\n"
                f"Cert No: {cert.cert_no}\n"
                f"UUID público: {cert.public_uuid}\n"
            )
            email_message = EmailMessage(
                subject=f"[CERTIFICACION PENDIENTE] {claim.full_name} - {cert.course.title}",
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
                reply_to=[claim.email] if claim.email else None,
            )
            email_message.send(fail_silently=False)
            messages.success(
                request,
                "Formulario enviado correctamente. Un administrador se contactará con usted."
            )
            return redirect("certifications:my_certificates_list")
    else:
        form = BecadoCertificateRequestForm(instance=existing_request, initial=initial)

    return render(
        request,
        "certifications/certificate_claim_form.html",
        {
            "certificate": cert,
            "form": form,
        },
    )


@login_required
@require_POST
def certificate_authorize(request, uuid):
    if not (request.user.is_staff or request.user.is_superuser):
        raise Http404("No encontrado")

    cert = get_object_or_404(Certificate, uuid=uuid)
    cert.pending = False
    cert.save(update_fields=["pending"])

    claim = getattr(cert, "becado_request", None)
    if claim:
        claim.status = BecadoCertificateRequest.Status.AUTHORIZED
        claim.authorized_at = timezone.now()
        claim.authorized_by = request.user
        claim.save(update_fields=["status", "authorized_at", "authorized_by"])

    messages.success(request, f"Certificación autorizada para {cert.user.get_full_name() or cert.user.username}.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("courses:course_admin_list")

def certificate_pdf_download(request, uuid):
    # Stub: render the same template; swap to real PDF generation if needed
    cert = get_object_or_404(Certificate.objects.select_related("user", "course"), public_uuid=uuid)
    ctx = _certificate_template_context(cert)
    return render(request, "certifications/certificate.html", ctx)

class CertificateUpdateByUUIDView(CertificateUpdateView):
    def get_object(self, queryset=None):
        return get_object_or_404(Certificate, uuid=self.kwargs.get("uuid"))

class CertificateDeleteByUUIDView(CertificateDeleteView):
    def get_object(self, queryset=None):
        return get_object_or_404(Certificate, uuid=self.kwargs.get("uuid"))

class UserCertificateDetailByUUIDView(UserCertificateDetailView):
    def get_object(self, queryset=None):
        obj = get_object_or_404(Certificate, uuid=self.kwargs.get("uuid"))
        if obj.user_id != self.request.user.id and not self.request.user.is_staff:
            raise Http404()
        if obj.pending and not self.request.user.is_staff:
            raise Http404()
        return obj


# ---- In-person certificates (minimal stubs) ----
    # In-person views removed. ReportActivity is managed in the 'home' app.


# ---- Online Certificate Reports CRUD ----

class OnlineCertificateReportCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = OnlineCertificateReport
    form_class = OnlineCertificateReportForm
    template_name = "certifications/online_certificate_report_form.html"
    success_url = reverse_lazy("certifications:online_report_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "create"
        ctx["report"] = None
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Reporte creado exitosamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Error al crear el reporte: {form.errors}")
        return super().form_invalid(form)


class OnlineCertificateReportListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = OnlineCertificateReport
    template_name = "certifications/online_certificate_report_list.html"
    context_object_name = "reports"
    paginate_by = 10

    def get_queryset(self):
        # Sync course/year online rows from real certificates before listing CRUD data.
        get_online_certificates_by_course_year(limit_years=6)
        queryset = OnlineCertificateReport.objects.select_related("course").order_by("-issued_year", "course__title")
        year = self.request.GET.get("year")
        if year and year.isdigit():
            queryset = queryset.filter(issued_year=int(year))
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["fields"] = [
            "course",
            "issued_year",
            "cycle_start_date",
            "cycle_end_date",
            "is_closed",
            "sync_enabled",
            "districts_list",
            "regional_list",
            "province_list",
            "country_list",
            "total_quantity",
            "missing_location_count",
        ]
        ctx["selected_year"] = self.request.GET.get("year", "")
        ctx["available_years"] = (
            OnlineCertificateReport.objects.order_by("-issued_year")
            .values_list("issued_year", flat=True)
            .distinct()
        )
        return ctx


class OnlineCertificateReportDetailView(DetailView):
    model = OnlineCertificateReport
    template_name = "certifications/online_certificate_report_detail.html"
    context_object_name = "report"


class OnlineCertificateReportUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = OnlineCertificateReport
    form_class = OnlineCertificateReportForm
    template_name = "certifications/online_certificate_report_form.html"
    success_url = reverse_lazy("certifications:online_report_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = "update"
        ctx["report"] = self.object
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Reporte actualizado exitosamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Error al actualizar el reporte: {form.errors}")
        return super().form_invalid(form)


class OnlineCertificateReportDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = OnlineCertificateReport
    template_name = "certifications/online_certificate_report_confirm_delete.html"
    success_url = reverse_lazy("certifications:online_report_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["report"] = self.object
        return ctx

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Reporte eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)
