"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join
import sys


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
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'openedx.core.djangoapps.content.course_overviews',
    'organizations',
    'course_access_groups',
]

LOCALE_PATHS = [
    root('course_access_groups', 'conf', 'locale'),
]

REST_FRAMEWORK = {
    'PAGE_SIZE': 20
}

ROOT_URLCONF = 'course_access_groups.urls'

SECRET_KEY = 'insecure-secret-key'
