# scripts/test_smtp.py
from django.core.mail import send_mail
from django.conf import settings

def test_smtp():
    print("Host:", settings.EMAIL_HOST)
    print("Usuario:", settings.EMAIL_HOST_USER)

    try:
        send_mail(
            'Correo de prueba',
            'Este es un correo de prueba desde el script de Django.',
            settings.EMAIL_HOST_USER,
            ['jansgreen@gmail.com'],  # Reemplaza con el email de destino
            fail_silently=False,
        )
        print("Correo enviado correctamente.")
    except Exception as e:
        print("Error al enviar el correo:", e)
