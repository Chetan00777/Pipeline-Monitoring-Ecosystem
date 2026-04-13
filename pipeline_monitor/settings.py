# ============================================================
# Django Settings — Oil & Gas Pipeline Integrity Monitor
# ============================================================
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-pipeline-monitor-secret-key-change-in-prod')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'sensors',
    'fog_node',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pipeline_monitor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'pipeline_monitor.wsgi.application'

# DATABASE — SQLite (lightweight, perfect for Cloud9 & local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'pipeline_data.db',
    }
}

# PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONALISATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC FILES
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS — allow all origins (Cloud9 development)
CORS_ALLOW_ALL_ORIGINS = True

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

# ============================================================
# AWS CONFIGURATION (loaded from .env file)
# ============================================================
AWS_ACCESS_KEY_ID     = config('AWS_ACCESS_KEY_ID',     default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_SESSION_TOKEN     = config('AWS_SESSION_TOKEN',     default='')
AWS_REGION_NAME       = config('AWS_REGION_NAME',       default='us-east-1')

# SQS Queue names
SQS_PIPELINE_QUEUE    = config('SQS_PIPELINE_QUEUE',    default='pipeline-sensor-data')
SQS_ALERT_QUEUE       = config('SQS_ALERT_QUEUE',       default='pipeline-alerts')

# DynamoDB Table name
DYNAMODB_TABLE_NAME   = config('DYNAMODB_TABLE_NAME',   default='PipelineData')

# FOG NODE SETTINGS
FOG_NODE_URL              = config('FOG_NODE_URL', default='http://127.0.0.1:8000/fog/ingest/')
SENSOR_DISPATCH_INTERVAL  = config('SENSOR_DISPATCH_INTERVAL', default=3, cast=int)  # seconds
