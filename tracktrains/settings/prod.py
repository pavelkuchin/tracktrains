from .base import *

# Settings which are specific for the production environment.
HOST = "trackseats.info"

DEBUG = False
TEMPLATE_DEBUG = DEBUG
TASTYPIE_FULL_DEBUG = DEBUG

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

ADMINS = (('Pavel Kuchin', 'pavel.s.kuchin@gmail.com'),)
MANAGERS = ADMINS

ALLOWED_HOSTS = [
    '.%s.' % HOST,
    '.%s' % HOST
]

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
            'level': get_env_var('LOG_LEVEL'),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': get_env_var('APP_ROOT') + '/logs/tracktrains.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'basic'
        },
    },
    'loggers': {
        '': {
            'level': get_env_var('LOG_LEVEL'),
            'handlers': ['file']
        },
        'django': {
            'level': get_env_var('LOG_LEVEL'),
            'propagate': True,
        }
    }
}
