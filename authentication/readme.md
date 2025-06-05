authentication/
│
├── admin.py
├── apps.py
├── forms/
│   ├── __init__.py
│   ├── login_form.py
│   ├── register_form.py
│   ├── profile_form.py
│   └── password_reset_forms.py
│
├── models/
│   ├── __init__.py
│   ├── profile.py
│   └── tokens.py  # si usas tokens personalizados
│
├── views/
│   ├── __init__.py
│   ├── auth_views.py
│   ├── profile_views.py
│   └── password_views.py
│
├── templates/
│   └── authentication/
│       ├── login.html
│       ├── register.html
│       ├── profile.html
│       ├── password_reset.html
│       └── confirm_email.html
│
├── urls.py
├── serializers.py (si usas API con DRF)
├── signals.py
├── permissions.py
├── decorators.py
├── tests/
│   ├── __init__.py
│   └── test_authentication.py
│
└── utils.py








├── models.py/
clientes clase
user “clase relacionada django.contrib.auth.models”
Address “relacionada”

Estudiantes clase
    user “clase relacionada django.contrib.auth.models”
    Address “relacionada”
    Grados
    Certificaciones
Staff clase
    user “clase relacionada django.contrib.auth.models”
    Address “relacionada”
    Niveles de accesos
    Biografia
Profile clase
    user “clase relacionada django.contrib.auth.models”
    Address “relacionada”

Address clase
    user “clase relacionada django.contrib.auth.models”
    casa y calle
    Barrio o sector
    Municipio
    Provincia
    Codigo Postal
