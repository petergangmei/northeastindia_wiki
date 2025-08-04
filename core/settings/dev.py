"""
Django development settings for northeastindia.wiki project.

These settings should be used during development only.
"""

import os
import dj_database_url
from .common import *
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b32dg98-gay)$=yk$!1z&1*ibvlyer%d5h9p22cmbgx)u8e5(g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Use DATABASE_URL_STAGE if available, otherwise fallback to SQLite
database_url = os.environ.get('DATABASE_URL_STAGE')
print('database_url--->',database_url)
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(database_url)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Additional development apps
INSTALLED_APPS += [
    # Add development specific apps here, like:
    # 'debug_toolbar',
]

# Additional development middleware
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# Development-specific logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Show emails in the console during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 