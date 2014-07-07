from .base import *

# Settings which are specific for the production environment.

DEBUG = False
TEMPLATE_DEBUG = DEBUG
TASTYPIE_FULL_DEBUG = DEBUG

ADMINS = (('Pavel Kuchin', 'pavel.s.kuchin@gmail.com'),)
MANAGERS = ADMINS

ALLOWED_HOSTS = [
    '.host.com.',
    '.host.com'
]

LOGGING = {}
