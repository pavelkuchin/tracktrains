from .base import *

# Settings which are specific for the local environment.
HOST = "localhost:8080"

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TASTYPIE_FULL_DEBUG = DEBUG

ADMINS = (('root', 'root@localhost'),)
MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/tracktrains-messages'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
      'basic': {
        'format': '%(levelname)s %(asctime)s %(message)s'
      }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/tracktrains.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'basic'
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['file']
        },
        'django': {
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}
