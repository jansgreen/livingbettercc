# utils/management/commands/update_routes.py
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from menu.models import Route


class Command(BaseCommand):
    help = 'Guarda las rutas disponibles en la base de datos'

    def handle(self, *args, **kwargs):
        resolver = get_resolver()
        added = 0
        for pattern in resolver.url_patterns:
            if pattern.name:  # solo si tiene name (para usar con reverse)
                path = str(pattern.pattern)
                route_obj, created = Route.objects.get_or_create(
                    name=pattern.name,
                    defaults={'path': path}
                )
                if created:
                    added += 1
        self.stdout.write(self.style.SUCCESS(f'{added} rutas nuevas agregadas.'))
