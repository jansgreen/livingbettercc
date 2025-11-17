from django.utils import timezone

from django.shortcuts import get_object_or_404, render
from .models import Certificate
from django.http import HttpResponse, FileResponse
from django.template.loader import get_template
import os
from django.contrib.auth.decorators import login_required

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
