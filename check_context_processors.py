import django
import os
from django.conf import settings
from importlib import import_module

# Inicializar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "livingbettercc.settings")  # <-- Cambia si tu settings tiene otro nombre
django.setup()

def test_context_processors():
    print("\n===== TESTEANDO CONTEXT PROCESSORS =====\n")

    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    for path in processors:
        print(f"Probando: {path}")

        try:
            # Cargar módulo
            module_path, func_name = path.rsplit('.', 1)
            module = import_module(module_path)
            func = getattr(module, func_name)

            # Ejecutar función simulando request vacío
            result = func(type('FakeRequest', (), {'user': None})())

            # Verificar tipo
            if not isinstance(result, dict):
                print(f" ❌ ERROR → {path} devuelve {type(result)}, NO un dict\n")
            else:
                print(f" ✅ OK → {path} devuelve dict\n")

        except Exception as e:
            print(f" ⚠️ EXCEPCIÓN en {path}: {e}\n")

    print("===== FIN =====")

if __name__ == "__main__":
    test_context_processors()
