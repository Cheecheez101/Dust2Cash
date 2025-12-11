import os
import importlib.util
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Security / environment-friendly defaults
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes') #false for production
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'dust2cash-b8e6.onrender.com,.vercel.app,127.0.0.1').split(',')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core.apps.CoreConfig',
]

# Detect whether whitenoise is installed so we can fail gracefully during builds
_USE_WHITENOISE = importlib.util.find_spec('whitenoise') is not None

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise will be inserted below only if installed
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if _USE_WHITENOISE:
    # Insert WhiteNoise right after SecurityMiddleware for static serving in production
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'dust2cash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.dust2cash_settings',
                'core.context_processors.user_portal',
                'core.context_processors.inject_agent_details',
            ],
        },
    },
]

WSGI_APPLICATION = 'dust2cash.wsgi.application'
# ------------uncomment for local use---------------#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL')
#     )
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static / Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'           # collectstatic target
STATICFILES_DIRS = [BASE_DIR / 'static']         # find app-level static/ during collectstatic

if _USE_WHITENOISE:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Fallback so collectstatic won't fail when whitenoise isn't installed in the build environment
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email config (defaults to console unless overridden in .env)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp-relay.brevo.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')

# Sendinblue / Brevo (SIB) settings - read from environment; leave console backend as default for dev
SIB_API_KEY = os.getenv('BREVO_API_KEY') or os.getenv('SIB_API_KEY')
SIB_SENDER_EMAIL = os.getenv('BREVO_SENDER_EMAIL') or os.getenv('SIB_SENDER_EMAIL')
SIB_SENDER_NAME = os.getenv('BREVO_SENDER_NAME') or os.getenv('SIB_SENDER_NAME') or 'Dust2Cash'

# Admin contact (used for contact form notifications)
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'support@michaelnganga.me')

# Default from email used by send_mail when no from_email provided
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', SIB_SENDER_EMAIL or 'support@michaelnganga.me')

# Celery / Redis configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_BEAT_SCHEDULE = {
    'expire-agent-requests-every-15-minutes': {
        'task': 'core.tasks.expire_agent_requests',
        'schedule': crontab(minute='*/15'),
    },
}

# put near end of settings.py
import logging
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'console': {'class': 'logging.StreamHandler'},
  },
  'root': {'handlers': ['console'], 'level': 'INFO'},
}
logging.getLogger().info('settings loaded, DEBUG=%s', DEBUG)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://dust2cash.onrender.com,https://*.vercel.app').split(',')
