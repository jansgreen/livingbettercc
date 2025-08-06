# signals.py o dentro de tu lógica
from certifications.models import Certificate
from enrollments.models import Enrollment

if Enrollment.completed and not hasattr(Enrollment, 'certificate'):
    Certificate.objects.create(enrollment=Enrollment)
