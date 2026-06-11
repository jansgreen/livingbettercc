from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
from django.contrib.messages import constants as messages
import dj_database_url
from google.oauth2 import service_account



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

DEBUG = _env_bool('DEBUG', default=False)

# Detección de entorno: Heroku define DYNO. También soportamos DJANGO_ENV=heroku.
IS_HEROKU = os.getenv("DYNO") is not None or os.getenv("DJANGO_ENV", "").strip().lower() == "heroku"

# Seguridad HTTPS: por defecto solo en producción/Heroku.
# Si quieres forzarlo en local (solo si realmente sirves HTTPS), exporta SECURE_MODE=1.
SECURE_MODE =  os.getenv("SECURE_MODE") is not None and os.getenv("SECURE_MODE").strip().lower() in {"1", "true", "yes", "y", "on"}

SECRET_KEY_CARDNET = os.getenv('SECRET_KEY_CARDNET')

if SECURE_MODE:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Permitir HTTP solo en desarrollo
if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_OAUTH2_CLIENT_SECRETS_JSON = os.path.join(BASE_DIR, "client_secret.json")
GOOGLE_OAUTH2_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_ESCRITORIO_APP')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

def _parse_hosts_csv(value: str) -> list[str]:
    hosts: list[str] = []
    for raw in (value or "").split(","):
        host = (raw or "").strip()
        if not host:
            continue
        host = host.replace("https://", "").replace("http://", "")
        host = host.split("/")[0]
        host = host.split(":")[0]
        if host:
            hosts.append(host)
    # Quitar duplicados preservando orden
    return list(dict.fromkeys(hosts))


_common_hosts = [
    "136.116.129.2",
    "136.116.129.21",
    "localhost",
    "127.0.0.1",

    "livingbettercc.herokuapp.com",
    ".herokuapp.com",

    "livingbettercc.com",
    "www.livingbettercc.com",
    "livingbettercc.info",
    "www.livingbettercc.info",
    "livingbettercc.net",
    "www.livingbettercc.net",
    "livingbettercc.org",
    "www.livingbettercc.org",
    "livingbettercc.xyz",
    "www.livingbettercc.xyz",

    ".livingbettercc.com",
    ".livingbettercc.info",
    ".livingbettercc.net",
    ".livingbettercc.org",
    ".livingbettercc.xyz",

    "livingbettercc-dev-5e915f7fc878.herokuapp.com",
    "livingbettercc-ba2163025eea.herokuapp.com",
]

_env_hosts = _parse_hosts_csv(os.getenv("HOSTS", ""))
_dev_hosts = _parse_hosts_csv(os.getenv("ALLOWED_HOSTS", ""))

ALLOWED_HOSTS = list(dict.fromkeys([*_env_hosts, *_dev_hosts, *_common_hosts]))

CSRF_TRUSTED_ORIGINS = [
    "https://livingbettercc.com",
    "https://www.livingbettercc.com",
    "https://livingbettercc.info",
    "https://www.livingbettercc.info",
    "https://livingbettercc.net",
    "https://www.livingbettercc.net",
    "https://livingbettercc.org",
    "https://www.livingbettercc.org",
    "https://livingbettercc.xyz",
    "https://www.livingbettercc.xyz",
    "https://livingbettercc.herokuapp.com",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'home',
    'classroom',
    'classroom.courses',
    'classroom.quicktest',
    'classroom.enrollments',
    'classroom.certifications',
    'authentication',
    'authentication.students',
    'authentication.address.apps.AddressConfig',
    'formbuilder',
    'shop',
    'gallery',
    'cart',
    'core',
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    'googleauth',
    'social_django',
    'dashboard',
    'dashboard.metadata',
    'authentication.groups',
    'dashboard.contents',
    'django_ckeditor_5',
    'payments',

]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["openid", "profile", "email", "https://www.googleapis.com/auth/youtube.force-ssl"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

SITE_ID = 1 

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'classroom.middleware.RequireActiveEnrollmentMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', 
    'allauth.account.middleware.AccountMiddleware',

]

WHITENOISE_MANIFEST_STRICT = False

ROOT_URLCONF = 'livingbettercc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'home/templates'), 
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'home.context_processors.context_processor.bootstrap_css',
                'home.context_processors.context_processor.bootstrap_js',
                'home.context_processors.context_processor.obtener_menu_report_activity',

                # authentication
                'authentication.context_processors.context_processor.obtener_menu_auth',
                'authentication.context_processors.context_processor.obtener_menu_directives',
                'authentication.context_processors.context_processor.obtener_menu_messages',

                # formbuilder
                'formbuilder.context_processors.context_processor.obtener_formbuilder_menu',

                #shop and cart
                'shop.context_processors.context_processor.obtener_menu_shop',
                'cart.context_processors.context_processor.obtener_menu_cart',

                # Classroom
                'classroom.context_processors.context_processor.obtener_menu_classroom',
                'classroom.context_processors.context_processor.obtener_progress_class',
                'classroom.context_processors.context_processor.obtener_certificados_usuario',

                # Dashboard
                'dashboard.context_processors.context_processor.obtener_menu_contents',
                'authentication.context_processors.context_processor.obtener_menu_groups',
                'dashboard.metadata.context_processors.context_processor.metadata_context',
                'dashboard.context_processors.context_processor.obtener_menu_dashboard',
                
                # Gallery
                'gallery.context_processors.context_processor.obtener_gallery_img',

                # QuickTest
                'classroom.quicktest.context_proccessors.context_proccessor.obtener_menu_quicktest',
                'payments.context_processors.context_processor.obtener_menu_payments',


            ],
        },
    },
]

# Evita forzar template debug en producción.

WSGI_APPLICATION = 'livingbettercc.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASE_URL = os.getenv("DATABASE_URL")

IS_HEROKU = os.getenv("DYNO") is not None


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=False,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

#if IS_HEROKU:
#    if not DATABASE_URL:
#        raise Exception("DATABASE_URL not defined in production.")
#    DATABASES = {
#        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
#    }
#else:
#    DATABASES = {
#        "default": {
#            "ENGINE": "django.db.backends.sqlite3",
#            "NAME": BASE_DIR / "db.sqlite3",
#        }
#    }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# WhiteNoise puede convertirlo en 500. Manténlo laxo para evitar caída total.
WHITENOISE_MANIFEST_STRICT = False

# Archivos de medios (subidos por los usuarios)


# Cloudinary Storage si está habilitado actualizado con google cloud storage
USE_CLOUDINARY = os.getenv("USE_CLOUDINARY", "false").lower() == "true"
USE_GCS = os.getenv("USE_GCS", "false").lower() == "true"
DEFAULT_GCS_CREDENTIALS_PATH = "/home/livingbettercc/spheric-wonder-449401-f5-a94a652cdc7b.json"

if USE_GCS:
    INSTALLED_APPS.append('storages')

if USE_GCS:
    google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", DEFAULT_GCS_CREDENTIALS_PATH)
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        google_credentials_path
    )
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if USE_CLOUDINARY and not CLOUDINARY_URL:
    USE_CLOUDINARY = False


GS_BUCKET_NAME = "livingbettercc-media-2026"


if USE_GCS:

    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/"

    STORAGES = {
        "default": {
            "BACKEND": "core.storage.SafeGoogleCloudStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

elif USE_CLOUDINARY:

    MEDIA_URL = ""

    CLOUDINARY_STORAGE = {
        "SECURE": True,
        "PREFIX": "",
    }

    STORAGES = {
        "default": {
            "BACKEND": "core.storage.MixedMediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

else:

    MEDIA_URL = "/media/"

    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }



MEDIA_ROOT = os.path.join(BASE_DIR, "media")
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024

# Loguea errores de requests a consola (aparece en heroku logs)
if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "root": {"handlers": ["console"], "level": "INFO"},
        "loggers": {
            "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": True},
            # Captura específicamente DisallowedHost / SuspiciousOperation
            "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


if DEBUG:
    # Configuración de desarrollo
    BOOTSTRAP_CSS = os.path.join(STATIC_URL, 'bootstrap/css/bootstrap.css')
    BOOTSTRAP_JS = os.path.join(STATIC_URL, 'bootstrap/js/bootstrap.bundle.js')

else:
    # Configuración de producción
    BOOTSTRAP_CSS = os.path.join(STATIC_URL,'bootstrap/css/bootstrap.min.css')
    BOOTSTRAP_JS = os.path.join(STATIC_URL,'bootstrap/js/bootstrap.bundle.min.js')

# Configurar el framework de mensajes
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
    }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_HOST_FROM_USER = os.getenv('EMAIL_HOST_FROM_USER')
EMAIL_HOST_CC = os.getenv('EMAIL_HOST_CC', '').split(',')
EMAIL_HOST_DEST = os.getenv('EMAIL_HOST_DEST')

# En settings.py
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/shop/'
LOGIN_URL = '/auth/login/'  # si tu url real es authentication/login/

PAYPAL_CLIENT_ID = 'tu_client_id'
PAYPAL_CLIENT_SECRET = 'tu_client_secret'
PAYPAL_MODE = 'sandbox'  # Cambia a 'live' para producción



# paypal
PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = 'livingbettecommunitycenter@gmail.com'
# django_ckeditor_5 provides the upload endpoint named "ck_editor_5_upload_file"
# (see include('django_ckeditor_5.urls') in the project urls).
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = "ck_editor_5_upload_file"
customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]

CKEDITOR_5_CONFIGS = {
        'default': {
            'toolbar': {
                'items': ['heading', '|', 'bold', 'italic', 'link',
                        'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
                        }

        },
        'extends': {
            'blockToolbar': [
                'paragraph', 'heading1', 'heading2', 'heading3',
                '|',
                'bulletedList', 'numberedList',
                '|',
                'blockQuote',
            ],
            'toolbar': {
                'items': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                        'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                        'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                        'insertTable',
                        ],
                'shouldNotGroupWhenFull': 'true'
            },
            'image': {
                'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                            'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
                'styles': [
                    'full',
                    'side',
                    'alignLeft',
                    'alignRight',
                    'alignCenter',
                ]

            },
            'table': {
                'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties' ],
                'tableProperties': {
                    'borderColors': customColorPalette,
                    'backgroundColors': customColorPalette
                },
                'tableCellProperties': {
                    'borderColors': customColorPalette,
                    'backgroundColors': customColorPalette
                }
            },
            'heading' : {
                'options': [
                    { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                    { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                    { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                    { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
                ]
            }
        },
        'list': {
            'properties': {
                'styles': 'true',
                'startIndex': 'true',
                'reversed': 'true',
            }
        }
    }
