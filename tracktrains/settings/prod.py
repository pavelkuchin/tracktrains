from .base import *

# Settings which are specific for the production environment.
HOST = "trackseats.info"

DEBUG = False
TEMPLATE_DEBUG = DEBUG
TASTYPIE_FULL_DEBUG = DEBUG

# Security settings
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

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
            'maxBytes': 1024*1024*1, # 1 MB
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
