"""数据库配置"""
import os
from config import ENVIRONMENT

CONN_MAX_AGE = int(os.getenv("CONN_MAX_AGE", 60))

{% if cookiecutter.database_backend == "sqlite" %}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "db.sqlite3",
        ),
    }
}
{% elif cookiecutter.database_backend == "mysql" %}
from config.tools.mysql import get_mysql_settings

_name, _host, _port, _user, _password = get_mysql_settings()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": _name,
        "USER": _user,
        "PASSWORD": _password,
        "HOST": _host,
        "PORT": _port,
        "CONN_MAX_AGE": CONN_MAX_AGE,
        "OPTIONS": {"charset": "utf8mb4"},
    }
}
{% elif cookiecutter.database_backend == "postgresql" %}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "{{ cookiecutter.project_name }}"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": CONN_MAX_AGE,
    }
}
{% endif %}
