"""
Django settings for oss-request2 project.

"""

import os
import dj_database_url

#from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&6xw@t9%hcvo(^s5=cjarpox#h+n5rr@rl1*)de@bt1^s&qgz2'

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv("IN_DEVELOPMENT") == '1':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://oss-request2.sfdc.sh']

# Application definition

INSTALLED_APPS = [
    'myapp.apps.MyappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'allauth.socialaccount.providers.slack',
    'rest_framework',
    'django.contrib.staticfiles',
    'django_q',
    'mysite',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'myapp..middleware.AuthenticationMiddleware',
    'django.contrib.auto_auth.middleware.AuthenticationMiddleware',
]



Q_CLUSTER = {
    'name': 'DjangORM',
    'timeout': 90,
    'retry': 180,
    'orm': 'default',
}

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'
#WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = ( os.path.join(BASE_DIR, 'static'), )

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# SLACK API Configurations
# ----------------------------------------------
# use your keys
CLIENT_ID = '1814240140212.2647654924209'
#OAUTH_ACCESS_TOKEN='xoxb-1814240140212-2628342876662-liTewS1U4tH3pwNus8K0JNh7'
CLIENT_SECRET = 'cc4c8e034cdcc881b00572a8c10c984c'
VERIFICATION_TOKEN = 'W7njdbCXbbXKmN99EBFey39f'
BOT_USER_ACCESS_TOKEN = 'xoxb-1814240140212-2628342876662-liTewS1U4tH3pwNus8K0JNh7'

SAML_FOLDER = os.path.join(BASE_DIR, './saml')

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
