"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""


import sys
from os.path import abspath, dirname, join
from os import environ

DEBUG = True


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


sys.path.append(root('mocks'))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'rest_framework',
    'mocks',
    'student',
    'openedx.core.djangoapps.content.course_overviews',
    'organizations',
    'tahoe_sites',
    'course_access_groups',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOCALE_PATHS = [
    root('course_access_groups', 'conf', 'locale'),
]

REST_FRAMEWORK = {
    'PAGE_SIZE': 20,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

FEATURES = {  # Mock the edX Platform features.
    'ORGANIZATIONS_APP': True,  # This app depends on the Organizations App.
}

ALLOWED_HOSTS = ['*']

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

STATIC_URL = '/static/'

ROOT_URLCONF = 'mocks.urls'

SECRET_KEY = 'insecure-secret-key'

# We can only run tests with a known flag value
TAHOE_SITES_USE_ORGS_MODELS = environ.get('TAHOE_SITES_USE_ORGS_MODELS')
if TAHOE_SITES_USE_ORGS_MODELS is None:
    raise ValueError('Please set TAHOE_SITES_USE_ORGS_MODELS value in your test environment')
if isinstance(TAHOE_SITES_USE_ORGS_MODELS, str):
    TAHOE_SITES_USE_ORGS_MODELS = (TAHOE_SITES_USE_ORGS_MODELS.lower() == 'true')
if not isinstance(TAHOE_SITES_USE_ORGS_MODELS, bool):
    raise TypeError('Bad datatype for TAHOE_SITES_USE_ORGS_MODELS')
FEATURES['TAHOE_SITES_USE_ORGS_MODELS'] = TAHOE_SITES_USE_ORGS_MODELS
