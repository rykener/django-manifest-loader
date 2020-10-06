from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / 'tests'

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'manifest_loader',
    'tests',
]

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'dist'
]

MANIFEST_LOADER = {}

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