# -*- coding: utf-8 -*-
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'loggy',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

SITE_ID = 1
APP_PATH = os.path.join(os.path.dirname(__file__), "..")
MEDIA_ROOT = os.path.join(APP_PATH, "media")
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(APP_PATH, "media/static")
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = '0#z5xwjah13&amp;sbi1d=5ci$y5$y!9y=_ksdp1$w5*-u7c=qv!l7'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sloggy.urls'

WSGI_APPLICATION = 'sloggy.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(APP_PATH, "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    # "django.contrib.auth.context_processors.auth",
    'django.core.context_processors.request',
    "django.core.context_processors.debug",
    # "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    #"django.core.context_processors.static",
    #"django.contrib.messages.context_processors.messages",

    # my
    "main.context_processors.settings.settings_processor",
    "main.context_processors.cookies.cookies_processor",
    "logs.context_processors.sidebar.sidebar_processor"
)

INSTALLED_APPS = (
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.admin',
    # 'django.contrib.admindocs',
    'main',
    'logs'
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console',],
            'level': 'DEBUG'
        }
    }
}

# Custom
GROUPS_PER_PAGE = 30
LOGS_PER_PAGE = 30
DB_PREFIX = ""  # don't forget to change in clients
VERSION = "0.3"

try:
    from local_settings import *
except ImportError:
    pass
