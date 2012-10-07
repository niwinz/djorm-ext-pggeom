import os, sys

sys.path.insert(0, '..')
sys.path.insert(0, '/home/niwi/devel/djorm-ext-core')
sys.path.insert(0, '/home/niwi/devel/djorm-ext-expressions')

PROJECT_ROOT = os.path.dirname(__file__)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_DIRS = ()

SECRET_KEY = 'di!n($kqa3)nd%ikad#kcjpkd^uw*h%*kj=*pm7$vbo6ir7h=l'
INSTALLED_APPS = (
    'djorm_core',
    'djorm_expressions',
    'pg_geometric',
    'djorm_pggeom',
)
