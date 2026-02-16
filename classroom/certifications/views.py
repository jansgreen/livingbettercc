from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.http import Http404
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Certificate
from .forms import CertificateForm
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
        return Certificate.objects.select_related("course").filter(user=self.request.user).order_by("-issued_date")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_becado"] = self.request.user.groups.filter(name="students_becados").exists()
        return ctx


# certifications/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from classroom.certifications.models import Certificate


class UserCertificateDetailView(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = "certifications/certificate.html"
    context_object_name = "certificate"

    # Si tu URL usa uuid: path("my/<uuid:uuid>/", UserCertificateDetailView.as_view(), ...)
    def get_object(self, queryset=None):
        uuid = self.kwargs.get("uuid")
        cert = get_object_or_404(Certificate, uuid=uuid, user=self.request.user)
        return cert

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Alias para que el template funcione si usas "certificado"
        ctx["certificado"] = ctx["certificate"]

        # Datos extra útiles para el certificado (opcionales)
        user = ctx["certificate"].user
        ctx["student_name"] = (user.get_full_name() or user.username).strip()
        ctx["course_title"] = ctx["certificate"].course.title
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
    is_becado = user.groups.filter(name="students_becados").exists()
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

def certificate_public_view(request, uuid):
    cert = get_object_or_404(Certificate, public_uuid=uuid)
    if cert.pending and not (request.user.is_authenticated and request.user.is_staff):
        raise Http404("No encontrado")
    ctx = {
        "certificate": cert,
        "certificado": cert,
        "cert_left_ref": getattr(settings, "CERT_LEFT_REF", None),
        "cert_right_ref": getattr(settings, "CERT_RIGHT_REF", None),
        "cert_brand": getattr(settings, "CERT_BRAND", None),
        "cert_sig1_name": getattr(settings, "CERT_SIG1_NAME", None),
        "cert_sig1_role": getattr(settings, "CERT_SIG1_ROLE", None),
        "cert_sig2_name": getattr(settings, "CERT_SIG2_NAME", None),
        "cert_sig2_role": getattr(settings, "CERT_SIG2_ROLE", None),
        "cert_quote": getattr(settings, "CERT_QUOTE", None),
    }
    return render(request, "certifications/certificate.html", ctx)


def certificate_toggle_pending(request, uuid):
    if not (request.user.is_authenticated and request.user.is_staff):
        raise Http404("No encontrado")
    cert = get_object_or_404(Certificate, uuid=uuid)
    cert.pending = not cert.pending
    cert.save(update_fields=["pending"])
    ctx = {
        "certificate": cert,
        "certificado": cert,
        "cert_left_ref": getattr(settings, "CERT_LEFT_REF", None),
        "cert_right_ref": getattr(settings, "CERT_RIGHT_REF", None),
        "cert_brand": getattr(settings, "CERT_BRAND", None),
        "cert_sig1_name": getattr(settings, "CERT_SIG1_NAME", None),
        "cert_sig1_role": getattr(settings, "CERT_SIG1_ROLE", None),
        "cert_sig2_name": getattr(settings, "CERT_SIG2_NAME", None),
        "cert_sig2_role": getattr(settings, "CERT_SIG2_ROLE", None),
        "cert_quote": getattr(settings, "CERT_QUOTE", None),
    }
    return render(request, "certifications/certificate.html", ctx)


def claim_certificate(request, uuid):
    if not request.user.is_authenticated:
        raise Http404("No encontrado")
    cert = get_object_or_404(Certificate, uuid=uuid, user=request.user)
    if not cert.pending:
        return redirect("certifications:my_certificates_list")

    is_becado = request.user.groups.filter(name="students_becados").exists()
    if not is_becado:
        raise Http404("No encontrado")

    profile = Profiles.objects.filter(user=request.user).first()
    student = Students.objects.filter(user=request.user).first()
    telefono = ""
    if profile and getattr(profile, "telefono", None):
        telefono = profile.telefono
    elif student and getattr(student, "telefono", None):
        telefono = student.telefono

    full_name = (request.user.get_full_name() or request.user.username).strip()
    to_emails = [getattr(settings, "EMAIL_HOST_DEST", settings.EMAIL_HOST_USER)]
    body = (
        "Solicitud de certificación (estudiante becado)\n\n"
        f"Nombre: {full_name}\n"
        f"Usuario: {request.user.username}\n"
        f"Email: {request.user.email}\n"
        f"Teléfono: {telefono}\n"
        f"Curso: {cert.course.title}\n"
        f"Cert No: {cert.cert_no}\n"
        f"UUID público: {cert.public_uuid}\n"
    )

    email_message = EmailMessage(
        subject=f"[CERTIFICACION] Reclamo de certificado - {full_name}",
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=to_emails,
        reply_to=[request.user.email] if request.user.email else None,
        cc=getattr(settings, "EMAIL_HOST_CC", None),
    )
    email_message.send(fail_silently=False)
    messages.success(request, "Solicitud enviada. Te contactaremos pronto.")
    return redirect("certifications:my_certificates_list")

def certificate_pdf_download(request, uuid):
    # Stub: render the same template; swap to real PDF generation if needed
    cert = get_object_or_404(Certificate, public_uuid=uuid)
    ctx = {
        "certificate": cert,
        "certificado": cert,
        "cert_left_ref": getattr(settings, "CERT_LEFT_REF", None),
        "cert_right_ref": getattr(settings, "CERT_RIGHT_REF", None),
        "cert_brand": getattr(settings, "CERT_BRAND", None),
        "cert_sig1_name": getattr(settings, "CERT_SIG1_NAME", None),
        "cert_sig1_role": getattr(settings, "CERT_SIG1_ROLE", None),
        "cert_sig2_name": getattr(settings, "CERT_SIG2_NAME", None),
        "cert_sig2_role": getattr(settings, "CERT_SIG2_ROLE", None),
        "cert_quote": getattr(settings, "CERT_QUOTE", None),
    }
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
        return obj


# ---- In-person certificates (minimal stubs) ----
    # In-person views removed. ReportActivity is managed in the 'home' app.
