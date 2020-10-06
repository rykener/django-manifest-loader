from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / 'tests'

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'manifest_loader',
    'tests',
]

STATICFILES_DIRS = [
    BASE_DIR / 'dist'
]

MANIFEST_LOADER = {}
