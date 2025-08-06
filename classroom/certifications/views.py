from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import get_object_or_404, render
from .models import Certificate
from django.http import HttpResponse
from django.template.loader import get_template
import weasyprint  # Asegúrate de tenerlo instalado

def certificate_public_view(request, uuid):
    certificate = get_object_or_404(Certificate, uuid=uuid)
    enrollment = certificate.enrollment
    context = {
        'certificate': certificate,
        'user': enrollment.user,
        'course': enrollment.course,
        'date': certificate.created_at,
    }
    return render(request, 'certificates/public_certificate.html', context)

def certificate_pdf_download(request, uuid):
    certificate = get_object_or_404(Certificate, uuid=uuid)
    template = get_template('certificates/pdf_template.html')
    html = template.render({'certificate': certificate})
    pdf_file = weasyprint.HTML(string=html).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{certificate.enrollment.user.username}.pdf"'
    return response
