"""
Django settings for mngcheck project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
import django_heroku
import logging.config
from icecream import ic

import rest_framework.permissions

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/



# Секретный ключ джанго берем из окружения при запуске на сервере
if os.environ.get("IN_SERVER"):
    SECRET_KEY = os.environ.get("SECRET_KEY")

else:
    SECRET_KEY = 'django-insecure-8fz9)#1la2o+1rfr!jo1j*+skk(3zq4b_++xb@c!p%(zy*r$zo'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if os.environ.get("No_DEBUG") else True

ALLOWED_HOSTS = ["web", "127.0.0.1"] if os.environ.get("IN_SERVER") is None else ["178.21.8.107", "kassbot.website"]



if os.environ.get("IN_SERVER"):
    # Stuff for when running in Docker-compose.
    DEFAULT_DOMAIN = 'https://{}'.format(ALLOWED_HOSTS[1])
    REDIS_PASS = ':'+'8d003412636c27bf33df1c0ae1379af0ca4f08a19eca09cc44a1008935e058e9'+'@'
    REDIS_HOST = '172.17.0.2'
    REDIS_PORT = '6379'
    #CELERY_BROKER_URL = 'redis://redis:6379/1'
    #CELERY_RESULT_BACKEND = 'redis://redis:6379/1'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': "mngcheck_db",
            'USER': 'postgres',
            'PASSWORD': '24e66d55acf7e0037817f460cfd5b107',
            'HOST': "172.17.0.2",
            'PORT': '5432',
        }
    }
    LOGGING_CONFIG = None
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join('/app/log/', 'djangolog.txt'),
                'formatter': 'app',
                'maxBytes': 1024*1024*15,   # 15MB
                'backupCount': 10,
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
        'formatters': {
            'app': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{'
            },
        },
    })
else:
    DEFAULT_DOMAIN = 'http://{}:8000'.format(ALLOWED_HOSTS[1])
    REDIS_PASS = ''
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = '6379'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Application definition

INSTALLED_APPS = [
    # Мои приложения
    'kkt_check',
    'users',
    'partners',
    'bot.apps.BotConfig',
    # Сторонние приложения
    'bootstrap4',
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


]

MIDDLEWARE = [
    #'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mngcheck.urls'

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

WSGI_APPLICATION = 'mngcheck.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases




# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

LANGUAGE_CODE = 'ru-RU'

# Пример вывода: 16 сентября 2012
DATE_FORMAT = 'd E Y'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# for sending mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'buh@5element35.ru'
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASS")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'buh@5element35.ru'
SERVER_EMAIL = 'buh@5element35.ru'

# REDIS related settings

CELERY_BROKER_URL = 'redis://' + REDIS_PASS + REDIS_HOST + ':' + REDIS_PORT+'/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT+'/0'


# Мои настройки
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/edit/'

# Activate Django-Heroku.
django_heroku.settings(locals())
