"""
Django common settings for northeastindia.wiki project.

These settings are shared across all environments.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Note that we need to go two levels up from this file
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third-party apps
    'storages',
    'import_export',
    'tinymce',
    'mptt',
    'taggit',
    
    # Custom apps
    'app',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom SEO middleware for URL redirects and canonical URLs
    'app.middleware.SEORedirectMiddleware',
    'app.middleware.CanonicalURLMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# TinyMCE Configuration - Using CDN to avoid S3 signed URL issues
TINYMCE_JS_URL = 'https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js'
TINYMCE_DEFAULT_CONFIG = {
    'height': 400,
    'width': '100%',
    'theme': 'silver',
    'menubar': 'file edit view insert format tools table help',
    'plugins': [
        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
        'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'media', 'table', 'paste', 'code', 'help', 'wordcount'
    ],
    'toolbar': [
        'undo redo | blocks | bold italic underline strikethrough | '
        'alignleft aligncenter alignright alignjustify | '
        'bullist numlist outdent indent | removeformat | help',
        'link unlink anchor | image media | table | '
        'charmap preview | searchreplace | '
        'visualblocks code fullscreen'
    ],
    'block_formats': 'Paragraph=p; Heading 1=h1; Heading 2=h2; Heading 3=h3; Heading 4=h4; Heading 5=h5; Heading 6=h6; Preformatted=pre',
    'content_style': '''
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: #151b25;
            max-width: none;
            margin: 0;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 { 
            font-family: 'Georgia', serif;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #151b25;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 0.3em;
        }
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.3em; }
        h4 { font-size: 1.1em; }
        p { margin-bottom: 1em; text-align: justify; }
        blockquote { 
            border-left: 4px solid #e10032;
            margin: 1em 0;
            padding: 0.5em 1em;
            background: #f8f9fa;
            font-style: italic;
        }
        code { 
            background: #f8f9fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
        }
        pre { 
            background: #f8f9fa;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #151b25;
        }
        a { color: #0645ad; text-decoration: none; }
        a:hover { text-decoration: underline; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }
        table, th, td {
            border: 1px solid #dee2e6;
        }
        th, td {
            padding: 0.75em;
            text-align: left;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
    ''',
    'paste_as_text': True,
    'invalid_elements': 'script,style,font,center',
    'image_advtab': True,
    'contextmenu': 'link image table',
    'resize': True,
    'statusbar': True,
    'branding': False,
    'promotion': False
} 