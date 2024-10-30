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
DEBUG = os.getenv('DEBUG')




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
    'catalog',
    'classroom',
    'payments',
    'ckeditor',
    'ckeditor_uploader',
    'blog',
    'authentication',
    'groups',
    'checkout',
    'page',
    'metadata',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'livingbettercc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'blog/templates'),
            os.path.join(BASE_DIR, 'home/templates'), 
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'home.context_processors.context_processor.bootstrap_css',
                'home.context_processors.context_processor.bootstrap_js',
                'blog.context_processors.context_processor.obtener_menus',
                'page.context_processors.context_processor.footer_context',
                'metadata.context_processors.context_processor.metadata_context',

            ],
        },
    },
]

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
    BOOTSTRAP_JS = os.path.join(STATIC_URL,'bootstrap/js/bootstrap.bundle.min.js')
    BOOTSTRAP_CSS = os.path.join(STATIC_URL,'bootstrap/css/bootstrap.min.css')

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "ckeditor_uploader.storage.models.ImageField"

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
LOGIN_REDIRECT_URL = 'catalog'
LOGOUT_REDIRECT_URL = 'home'


PAYPAL_CLIENT_ID = 'tu_client_id'
PAYPAL_CLIENT_SECRET = 'tu_client_secret'
PAYPAL_MODE = 'sandbox'  # Cambia a 'live' para producción

