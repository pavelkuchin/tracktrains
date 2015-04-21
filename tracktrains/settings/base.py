"""
Django settings for tracktrains project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os
from django.core.exceptions import ImproperlyConfigured

# Getting environment variables in right way
# (from two scoope of django 1.5 with minor changes)
def get_env_var(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

# source is https://snipt.net/kennethlove/django-absolute-paths-for-settingspy/
# here() gives us file paths from the root of the system to the directory
# holding the current file.
here = lambda * x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

PROJECT_ROOT = here("..")
# root() gives us file paths from the root of the system to whatever
# folder(s) we pass it starting at the parent directory of the current file.
root = lambda * x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)

# TODO check this and remove
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

SECRET_KEY = get_env_var('SECRET_KEY')

DEBUG = False
TEMPLATE_DEBUG = DEBUG
TASTYPIE_FULL_DEBUG = False

# Application definition
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'tastypie',
)

LOCAL_APPS = (
    'profiles',
    'utils',
    'watcher'
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware'
)

ROOT_URLCONF = 'tracktrains.urls'

WSGI_APPLICATION = 'tracktrains.wsgi.application'

AUTH_USER_MODEL = 'profiles.TrackTrainsUser'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tracktrains',
        'USER': get_env_var('DB_USER'),
        'PASSWORD': get_env_var('DB_PASS'),
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Minsk'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Uploaded files
MEDIA_ROOT = root('..', 'media')
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = root('..', 'static')
STATIC_URL = '/static/'

# Templates dir
TEMPLATE_DIRS = (root('..', 'templates'),)

# Front-End links
SIGNUP_PAGE = "signup"

# BYRW Job script settings
BYRW_BASE_URL = get_env_var('BYRW_BASE_URL')
BYRW_DATA_URL = get_env_var('BYRW_DATA_URL')
BYRW_NAMESPACE = get_env_var('BYRW_NAMESPACE')
BYRW_CITIES_URL = get_env_var('BYRW_CITIES_URL')
