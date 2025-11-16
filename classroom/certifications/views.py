from django.utils import timezone

from django.shortcuts import get_object_or_404, render
from .models import Certificate
from django.http import HttpResponse, FileResponse
from django.template.loader import get_template
import os
from .models import Certificate

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
    return render(request, 'certificates/public_certificate.html', context)


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
