"""
Django settings for rerunsdjango project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os

# Horrific workaround to issue with Beanstalk: via
# https://stackoverflow.com/questions/75037873/problem-with-sqlite-when-deploying-django-website-on-aws-cant-properly-install
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

IS_TESTING = 'RDS_DB_NAME' not in os.environ

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = IS_TESTING

if IS_TESTING:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
else:
    ALLOWED_HOSTS = [
        "reruns-django-env.eba-kzy9sugh.us-east-1.elasticbeanstalk.com",
        ".reruns-django-env.eba-kzy9sugh.us-east-1.elasticbeanstalk.com",
        os.environ["PRIVATE_IP"],
        os.environ["ALLOW_HOST"],
    ]


INTERNAL_IPS = [
    "127.0.0.1",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "debug_toolbar",
    "django.contrib.sites", # required for invitations
    "invitations",
    "reruns",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "rerunsdjango.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "rerunsdjango.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if not IS_TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }




# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Eastern"

USE_I18N = True

USE_TZ = True


# Default format for inputting datetimes
# (Leave out seconds, celery beat isn't that precise anyway)

DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M"
]

# DATE_INPUT_FORMATS = [
#     "%Y-%m-%d %H:%M"
# ]

# TIME_INPUT_FORMATS = [
#      "%H:%M",
#      "%H:%M %P",
# ]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "assets"),
)


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Point Celery to Redis and the database
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
# db+postgresql://scott:tiger@localhost/mydatabase
# postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
# CELERY_RESULT_BACKEND = "".join([
#         "db+postgresql+psycopg2://",
#         os.environ['RDS_USERNAME'],
#         ":",
#         os.environ['RDS_PASSWORD'],
#         "@",
#         os.environ['RDS_HOSTNAME'],
#         ":",
#         os.environ['RDS_PORT']
#         "/",
#         os.environ['RDS_DB_NAME']
# ])

# Schedules will be stored in Django's own backend and show up nicely in /admin
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# For django-invitations:
# https://django-invitations.readthedocs.io/en/latest/installation.html
if IS_TESTING:
    SITE_ID = 1
else:
    SITE_ID = 2

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTH_USER_MODEL = "accounts.CustomUser"

# TODO: actually make it possible to send email
# https://docs.djangoproject.com/en/4.0/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
