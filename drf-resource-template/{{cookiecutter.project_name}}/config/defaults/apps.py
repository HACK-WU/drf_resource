"""Django 核心配置"""
import os
from config import BASE_DIR, PROJECT_ROOT, ENVIRONMENT

DEBUG = ENVIRONMENT == "development"
ALLOWED_HOSTS = ["*"]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_resource",
    {% if cookiecutter.enable_cors == "yes" %}
    "corsheaders",
    {% endif %}
    {% if cookiecutter.enable_celery == "yes" %}
    "django_celery_beat",
    "django_celery_results",
    {% endif %}
    {% if cookiecutter.enable_api_docs == "yes" %}
    "drf_spectacular",
    {% endif %}
    "{{ cookiecutter.project_name }}.apps.example",
]

MIDDLEWARE = [
    {% if cookiecutter.enable_cors == "yes" %}
    "corsheaders.middleware.CorsMiddleware",
    {% endif %}
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    {% if cookiecutter.enable_i18n == "yes" %}
    "django.middleware.locale.LocaleMiddleware",
    {% endif %}
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "{{ cookiecutter.project_name }}.urls"
WSGI_APPLICATION = "{{ cookiecutter.project_name }}.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_ROOT, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                {% if cookiecutter.enable_i18n == "yes" %}
                "django.template.context_processors.i18n",
                {% endif %}
            ],
        },
    },
]

USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
