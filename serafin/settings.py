'''
Django settings for the serafin project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
'''
import os
from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _
# from multisite import SiteID


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET', 'change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))
TEMPLATE_DEBUG = DEBUG
USERDATA_DEBUG = DEBUG

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = []

ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS.extend(ALLOWED_HOSTS_ENV.split(','))


# Application definition

# SITE_ID = SiteID(default=int(os.getenv('DEFAULT_SITE', 1)))
SITE_ID = int(os.getenv('DEFAULT_SITE', 1))

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_user_agents',
    'django.db.models',
    'request',
    'adminsortable',

    'codelogs',
    'tokens',
    'users',
    'tasker',
    'events',
    'content',
    'plumbing',
    'system',

    'filer',
    'serafin.apps.SuitConfig',
    'django.contrib.admin',
    'sitetree',
    'django_extensions',
    'rules.apps.AutodiscoverRulesConfig',
    'rest_framework',
    'mptt',
    # 'multisite',
    'easy_thumbnails',
    'huey.contrib.djhuey',
    'import_export',
    'compressor',
    'reversion',
    'constance',
    # 'raven.contrib.django.raven_compat',

    'serafin.apps.SerafinReConfig',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'users.middleware.AuthenticationMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'events.middleware.EventTrackingMiddleware',
    'request.middleware.RequestMiddleware',
)

ROOT_URLCONF = 'serafin.urls'

WSGI_APPLICATION = 'serafin.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django_settings_export.settings_export',
                'django.template.context_processors.static',
                # 'users.context_processors.add_support_email',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'NAME': os.getenv('POSTGRES_DB', 'serafin'),
        'USER': os.getenv('POSTGRES_USER', 'serafin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en')

LANGUAGES = (
    ('en', _('English')),
    ('nb', _('Norwegian')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'conf/locale'),
)

TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Oslo')
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_HTTPS = bool(int(os.getenv('USE_HTTPS', 0)))

if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/app/static'
COMPRESS_ENABLED = True

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

NPM_FILE_PATTERNS = {
}

THUMBNAIL_ALIASES = {
    '': {
        'small': {
            'size': (150, 150),
        },
        'medium': {
            'size': (739, 739),
        },
    }
}

THUMBNAIL_QUALITY = 90
THUMBNAIL_PRESERVE_EXTENSIONS = ('png',)
THUMBNAIL_TRANSPARENCY_EXTENSION = 'png'

FILER_DUMP_PAYLOAD = True


# User model and authentication

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.TokenBackend',
)

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

HOME_URL = '/home'
REGISTER_URL = '/register'

TOKEN_TIMEOUT_DAYS = 1
SESSION_COOKIE_NAME = 'serafin_session'
SESSION_COOKIE_AGE = 24 * 60 * 60  # 24 hours

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'users.backends.DigitPasswordValidator',
    },
]

# Events

LOG_USER_DATA = True
LOG_DEVICE_ON_LOGIN = True
LOG_TIME_PER_PAGE = True
LOG_MAX_MILLISECONDS = 5 * 60 * 1000  # 5 minutes


# Email

EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 25))
EMAIL_USE_TLS = bool(int(os.getenv('EMAIL_USE_TLS', 0)))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'Serafin <post@example.com>')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Serafin <post@example.com>')
EMAIL_SUBJECT_PREFIX = os.getenv('EMAIL_SUBJECT_PREFIX', '[Serafin]')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')


# SMS

SMS_SERVICE = os.getenv('SMS_SERVICE', 'Console')


# Google Analytics

GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', '')


# Huey

HUEY = {
    'name': 'serafin',
    'store_none': True,
    'always_eager': False,
    'immediate': True,
    'consumer': {
        'quiet': True,
        'workers': 100,
        'worker_type': 'greenlet',
        'health_check_interval': 60,
    },
    'connection': {
        'host': os.getenv('REDIS_HOST', 'redis'),
        'port': int(os.getenv('REDIS_PORT', 6379))
    }
}


# REST Framework

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        'rest_framework.permissions.AllowAny',
    ]
}


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s ' +
                      '%(process)d %(thread)d %(message)s'
        }
    },
    'filters': {
        'require_debug': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'serafin.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 0,
            'formatter': 'verbose',
            'encoding': 'utf-8'
        },
        'huey': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'huey.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 0,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
            'propagate': False
        },
        'django.request': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
            'propagate': False
        },
        'huey.consumer': {
            'handlers': ['huey'],
            'level': 'INFO',
            'propagate': True,
        },
        'debug': {
            'level': 'DEBUG',
            'handlers': ['debug'],
            'propagate': False
        }
    }
}


# Variables

RESERVED_VARIABLES = [
    {
        'name': 'email',
        'admin_note': 'Do not use in conditions. Used in registration.',
        'domains': []
    },
    {
        'name': 'phone',
        'admin_note': 'Do not use in conditions. Used in registration.',
        'domains': []
    },
    {
        'name': 'secondary_phone',
        'admin_note': 'Do not use in conditions. Used in registration.',
        'domains': []
    },
    {
        'name': 'password',
        'admin_note': 'Do not use in conditions. Used in registration.',
        'domains': []
    },
    {
        'name': 'force_change_password',
        'admin_note': 'Force the user to change their password.',
        'domains': []
    },
    {
        'name': 'registered',
        'admin_note': 'Returns True if the user is registered',
        'domains': ['user']
    },
    {
        'name': 'enrolled',
        'admin_note': 'Returns True if the user is enrolled with the current Program',
        'domains': ['user']
    },
    {
        'name': 'group',
        'admin_note': 'Returns a list of the Groups the user is a member of',
        'domains': ['user']
    },
    {
        'name': 'current_day',
        'admin_note': 'Returns the current localized weekday as number, where Monday is 1 and Sunday is 7',
        'domains': ['user']
    },
    {
        'name': 'current_time',
        'admin_note': 'Returns the current localized time in iso format, i.e. 12:00:00',
        'domains': ['user']
    },
    {
        'name': 'current_date',
        'admin_note': 'Returns the current localized date in iso format, i.e. 2015-05-01',
        'domains': ['user']
    },
    {
        'name': 'session',
        'admin_note': 'For system use. Returns the id of the current Session.',
        'domains': []
    },
    {
        'name': 'node',
        'admin_note': 'For system use. Returns the current node id (relative to Session).',
        'domains': []
    },
    {
        'name': 'stack',
        'admin_note': 'For system use. Returns a list of stacked (session, node) id pairs.',
        'domains': []
    },
    {
        'name': 'login_link',
        'admin_note': 'For system use. Used in processing login e-mails.',
        'domains': []
    },
    {
        'name': 'reply_session',
        'admin_note': 'For system use. Returns the session to transition from when receiving an SMS reply.',
        'domains': []
    },
    {
        'name': 'reply_node',
        'admin_note': 'For system use. Returns the node to transition from when receiving an SMS reply.',
        'domains': []
    },
    {
        'name': 'reply_variable',
        'admin_note': 'For system use. Returns the name of the last SMS reply variable.',
        'domains': []
    },
    {
        'name': 'timer',
        'admin_note': 'For system use, never accessible. Used for timing page visits.',
        'domains': []
    },
    {
        'name': 'tools',
        'admin_note': 'For the available tools of the user',
        'domains': []
    }
]


# Sandbox

SANDBOX_URL = os.getenv('SANDBOX_URL', '')
SANDBOX_PORT = os.getenv('SANDBOX_PORT', '')
SANDBOX_PATH = os.getenv('SANDBOX_PATH', '')
SANDBOX_API_KEY = os.getenv('SANDBOX_API_KEY', '')


# Available stylesheets for the dynamic switcher

STYLESHEETS = [
    {'name': _('Default stylesheet'), 'path': 'css/style.css'},
    {'name': _('Nalokson'), 'path': 'css/style-nalokson.css'},
    {'name': _('Miksmaster'), 'path': 'css/style-miksmaster.css'},
    {'name': _('Miksmaster alternate'),
     'path': 'css/style-miksmaster-alt.css'},
]

STYLESHEET_CHOICES = [(ss['path'], ss['name']) for ss in STYLESHEETS]


# Constance

CONSTANCE_CONFIG = OrderedDict([
    ('USER_VARIABLE_PROFILE_ORDER', (
        'session, node, stack, reply_session, reply_node, reply_variable',
        'What user variables to list first on a user\'s object page (comma separated)',
        str
    )),
    ('USER_VARIABLE_EXPORT', (
        '',
        'What user variables to export from user listing (comma separated, leave blank for all)',
        str
    )),
])

CONSTANCE_REDIS_CONNECTION = {
    'host': os.getenv('REDIS_HOST', 'redis'),
    'port': int(os.getenv('REDIS_PORT', 6379))
}


# Request

REQUEST_IGNORE_PATHS = (
    r'^admin',
    r'^static',
    r'^api.*(?<!users_stats)$',
)

REQUEST_IGNORE_USER_AGENTS = (
    r'^$',  # ignore blank user agent
    r'Googlebot',
    r'bingbot',
    r'YandexBot',
    r'MJ12Bot',
    r'Slurp',
    r'Baiduspider',
)

REQUEST_TRAFFIC_MODULES = (
    'request.traffic.UniqueVisitor',
    'request.traffic.UniqueUser',
    'request.traffic.Error',
    'request.traffic.Error404',
)

REQUEST_PLUGINS = (
    'request.plugins.TrafficInformation',
    'request.plugins.TopReferrers',
    'request.plugins.TopSearchPhrases',
    'request.plugins.TopBrowsers',
)


try:
    from .local_settings import *
except ImportError:
    pass


SETTINGS_EXPORT = [
    'DEBUG',
    'GOOGLE_ANALYTICS_ID',
]
