# myapp/management/commands/test_smtp.py
from django.core.management.base import BaseCommand
from scripts.test_smtp import test_smtp  # Importa la función desde el script

class Command(BaseCommand):
    help = 'Prueba el envío de correos usando la configuración SMTP'

    def handle(self, *args, **kwargs):
        test_smtp()
