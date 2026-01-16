from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.shortcuts import get_object_or_404, render
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.http import Http404

from .models import Certificate
from .forms import CertificateForm


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


# certifications/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from classroom.certifications.models import Certificate


class UserCertificateDetailView(LoginRequiredMixin, DetailView):
    model = Certificate
    template_name = "certifications/my_certificate_detail.html"
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
    """Create or get a certificate for a (user, course) pair, idempotent."""
    with transaction.atomic():
        try:
            cert, _created = Certificate.objects.get_or_create(
                user=user,
                course=course,
                defaults={"issued_date": timezone.now().date()},
            )
        except IntegrityError:
            cert = Certificate.objects.get(user=user, course=course)
    return cert

def certificate_public_view(request, uuid):
    cert = get_object_or_404(Certificate, uuid=uuid)
    return render(request, "certifications/certificate.html", {"certificate": cert})

def certificate_pdf_download(request, uuid):
    # Stub: render the same template; swap to real PDF generation if needed
    cert = get_object_or_404(Certificate, uuid=uuid)
    return render(request, "certifications/certificate.html", {"certificate": cert})

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
