from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
from django.contrib.messages import constants as messages

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

SECRET_KEY_CARDNET = os.getenv('SECRET_KEY_CARDNET')

# Permitir HTTP solo en desarrollo
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_OAUTH2_CLIENT_SECRETS_JSON = os.path.join(BASE_DIR, "client_secret.json")
GOOGLE_OAUTH2_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_ESCRITORIO_APP')

if os.getenv("DJANGO_ENV") == "heroku":
    ALLOWED_HOSTS = os.getenv("HOSTS", "").split(",")
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'classroom',
    'classroom.courses',
    'classroom.quicktest',
    'classroom.enrollments',
    'classroom.certifications',
    'authentication',
    'authentication.students',
    'authentication.formbuilder',
    'shop',
    'shop.checkout',
    'gallery',
    'cart',
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    'googleauth',
    'social_django',
    'dashboard',
    'dashboard.metadata',
    'dashboard.groups',
    'dashboard.contents',
    'django_ckeditor_5',

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', 
    'allauth.account.middleware.AccountMiddleware',
]

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
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'home.context_processors.context_processor.bootstrap_css',
                'home.context_processors.context_processor.bootstrap_js',

                # authentication
                'authentication.context_processors.context_processor.obtener_menu_auth',
                'authentication.context_processors.context_processor.obtener_formbuilder_menu',
                'authentication.context_processors.context_processor.obtener_menu_directives',

                #shop and cart
                'shop.context_processors.context_processor.obtener_menu_shop',
                'cart.context_processors.context_processor.obtener_menu_cart',

                # Classroom
                'classroom.context_processors.context_processor.obtener_menu_classroom',
                'classroom.context_processors.context_processor.obtener_progress_class',
                'classroom.context_processors.context_processor.obtener_certificados_usuario',

                # Dashboard
                'dashboard.context_processors.context_processor.obtener_menu_contents',
                'dashboard.groups.context_processors.context_processor.obtener_menu_groups',
                'dashboard.metadata.context_processors.context_processor.metadata_context',
                'dashboard.context_processors.context_processor.obtener_menu_dashboard',
                
                # Gallery
                'gallery.context_processors.context_processor.obtener_gallery_img'


            ],
        },
    },
]

TEMPLATES[0]['OPTIONS']['debug'] = True

WSGI_APPLICATION = 'livingbettercc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Archivos de medios (subidos por los usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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
EMAIL_HOST_FROM_USER = os.getenv('EMAIL_HOST_FROM_USE')
EMAIL_HOST_CC = os.getenv('EMAIL_HOST_CC', '').split(',')
EMAIL_HOST_DEST = os.getenv('EMAIL_HOST_DEST')

# En settings.py
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/shop/'


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

CKEDITOR_5_CUSTOM_CSS = 'path_to.css'
CKEDITOR_5_FILE_STORAGE = "path_to_storage.CustomStorage"
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