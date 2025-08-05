"""
Django production settings for northeastindia.wiki project.

These settings should be used in production only.
"""

import os
import dj_database_url
from dotenv import load_dotenv
from .common import *
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
# In production, this should be set from environment variables
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'northeastindia.wiki',
    'www.northeastindia.wiki',
    '127.0.0.1',
    'localhost',
    # Add any other production domains here
]
TRUSTED_ORIGINS = [
    'https://northeastindia.wiki',
    'https://www.northeastindia.wiki',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://127.0.0.1:8000',
    'https://localhost:8000',
]

# Add CSRF trusted origins specifically
CSRF_TRUSTED_ORIGINS = TRUSTED_ORIGINS

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# In production, use PostgreSQL via DATABASE_URL_PROD or fallback to individual env vars
database_url = os.environ.get('DATABASE_URL_PROD')
print('database_url--->',database_url)
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
else:
    # Fallback to individual environment variables for backward compatibility
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', ''),
            'USER': os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# Security settings for production
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'

# Security settings disabled for local development

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Additional CSRF settings for local development
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # Allow non-HTTPS for local development
CSRF_FAILURE_VIEW = 'app.views.csrf_failure'  # Custom CSRF failure view for debugging

SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'



# Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django-error.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security.csrf': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}

# Static files configuration for S3 (Private Bucket)
# Configure S3 storage for static files with signed URLs
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-south-1')
AWS_DEFAULT_ACL = 'private'  # Private bucket - requires signed URLs
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = True  # Enable signed URLs for private bucket
AWS_QUERYSTRING_EXPIRE = int(os.environ.get('AWS_QUERYSTRING_EXPIRE', 3600))  # 1 hour default
# AWS_S3_SIGNATURE_VERSION = 's3v4'                                            
AWS_S3_ADDRESSING_STYLE = 'virtual'      

print('AWS_ACCESS_KEY_ID--->',AWS_ACCESS_KEY_ID)
print('AWS_SECRET_ACCESS_KEY--->',AWS_SECRET_ACCESS_KEY)
print('AWS_STORAGE_BUCKET_NAME--->',AWS_STORAGE_BUCKET_NAME)
print('AWS_S3_REGION_NAME--->',AWS_S3_REGION_NAME)
print('AWS_DEFAULT_ACL--->',AWS_DEFAULT_ACL)
print('AWS_S3_FILE_OVERWRITE--->',AWS_S3_FILE_OVERWRITE)
print('AWS_QUERYSTRING_AUTH--->',AWS_QUERYSTRING_AUTH)


# S3 Object parameters for static files
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Configure STORAGES setting for Django 5.2+
STORAGES = {
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "default_acl": AWS_DEFAULT_ACL,
            "file_overwrite": AWS_S3_FILE_OVERWRITE,
            "querystring_auth": AWS_QUERYSTRING_AUTH,
            "querystring_expire": AWS_QUERYSTRING_EXPIRE,
            "object_parameters": AWS_S3_OBJECT_PARAMETERS,
        },
    },
}

# Keep media files local for now
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@northeastindia.wiki') 