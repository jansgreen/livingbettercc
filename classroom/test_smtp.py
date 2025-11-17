# scripts/test_smtp.py
from django.core.mail import send_mail
from django.conf import settings

def test_smtp():
    try:
        send_mail(
            'Correo de prueba',
            'Este es un correo de prueba desde el script de Django.',
            settings.EMAIL_HOST_USER,
            ['jansgreen@gmail.com'],  # Reemplaza con el email de destino
            fail_silently=False,
        )
    except Exception as e:
        return f'Error al enviar el correo: {e}'
