# S-02：配置架构设计

> 父文档：[DESIGN.md](DESIGN.md) | 共享术语：四层+角色配置、功能开关、条件渲染

## 术语

| 术语 | 定义 |
|------|------|
| defaults/ | 功能模块化的默认配置，每个文件对应一个功能域 |
| overview.py | 配置概览索引，说明所有配置模块的用途 |
| role/ | 角色差异配置，不同角色（web/worker）可加载不同的 INSTALLED_APPS |
| DJANGO_ROLE | 环境变量，决定加载哪个角色配置（默认 "web"） |

## 现状（AS-IS）

- bk-monitor 的 `config/default.py` 为 1900 行单体文件
- 角色分离存在但强耦合蓝鲸 PaaS（role/web.py 493 行，role/worker.py 595 行）

## 方案（TO-BE）

### 设计原则

按功能域拆分为 13 个独立模块 + 2 个角色配置 + 概览索引。每个文件职责单一，开发者按文件名即可定位到目标配置。

### 配置文件与功能域映射

| 文件 | 功能域 | 包含的 Settings | 条件生成 |
|------|--------|-----------------|----------|
| `overview.py` | 配置索引 | 无（纯文档） | 否 |
| `defaults/apps.py` | Django 核心 | INSTALLED_APPS, MIDDLEWARE, TEMPLATES, DEBUG | 否 |
| `defaults/database.py` | 数据库 | DATABASES, CONN_MAX_AGE | 否 |
| `defaults/cache.py` | 缓存 | CACHES | 否 |
| `defaults/rest_framework.py` | REST API | REST_FRAMEWORK, DRF_RESOURCE | 否 |
| `defaults/celery.py` | 异步任务 | CELERY_BROKER_URL 等 | `enable_celery` |
| `defaults/cors.py` | 跨域 | CORS_ALLOW_ALL_ORIGINS | `enable_cors` |
| `defaults/i18n.py` | 国际化 | LANGUAGE_CODE, USE_I18N | `enable_i18n` |
| `defaults/api_docs.py` | API 文档 | SPECTACULAR_SETTINGS | `enable_api_docs` |
| `defaults/static_files.py` | 静态资源 | STATIC_URL, STATIC_ROOT | 否 |
| `defaults/session.py` | Session | SESSION_COOKIE_AGE | 否 |
| `defaults/logging.py` | 日志 | LOGGING | 否 |
| `defaults/env_override.py` | 环境变量覆盖 | SETTINGS_ 前缀 | 否 |
| `role/web.py` | Web 角色 | 增加 web 特定 INSTALLED_APPS + MIDDLEWARE | 否 |
| `role/worker.py` | Worker 角色 | 精简 INSTALLED_APPS（无 DRF/view）+ Celery | `enable_celery` |

---

### 1. config/__init__.py — 基础常量

文件：[`{{cookiecutter.project_name}}/config/__init__.py`](file:///config/__init__.py)

```python
"""项目基础常量"""
import os

APP_CODE = os.getenv("APP_CODE", "{{ cookiecutter.project_name }}")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

ENVIRONMENT = os.getenv("DJANGO_ENV", "development")
RUN_MODE = {
    "development": "DEVELOP",
    "testing": "TEST",
    "production": "PRODUCT",
}.get(ENVIRONMENT, "DEVELOP")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

{% if cookiecutter.enable_celery == "yes" %}
from config.celery import app as celery_app
__all__ = ["celery_app"]
{% endif %}
```

---

### 2. config/overview.py — 配置概览索引

文件：[`{{cookiecutter.project_name}}/config/overview.py`](file:///config/overview.py)

```python
"""
配置概览索引
================
本文件说明项目中所有配置模块的用途，供开发者快速定位。

配置加载顺序（settings.py）：
    1. config/__init__.py         → 基础常量
    2. config/defaults/           → 功能模块（apps, database, cache, …）
    3. config/role/{role}.py      → 角色差异（web / worker）
    4. config/{env}.py            → 环境差异（dev / stag / prod）
    5. 环境变量覆盖               → SETTINGS_ 前缀注入
    6. local_settings.py          → 开发环境个人覆盖

默认配置模块（config/defaults/）：
    apps.py            - Django 核心（INSTALLED_APPS, MIDDLEWARE, TEMPLATES）
    database.py        - 数据库配置（DATABASES, CONN_MAX_AGE）
    cache.py           - 缓存配置（CACHES）
    rest_framework.py  - REST Framework + drf_resource 配置
    static_files.py    - 静态资源配置（STATIC_URL, STATIC_ROOT）
    session.py         - Session 配置
    logging.py         - 日志配置（LOGGING）
    env_override.py    - 环境变量自动覆盖机制

条件生成的配置模块：
    celery.py          - Celery 异步任务（enable_celery）
    cors.py            - CORS 跨域（enable_cors）
    i18n.py            - 国际化（enable_i18n）
    api_docs.py        - API 文档（enable_api_docs）

角色配置（config/role/）：
    web.py             - Web 角色（添加 CORS/Celery/docs 到 INSTALLED_APPS）
    worker.py          - Worker 角色（精简 INSTALLED_APPS，仅 Celery + 核心）

环境差异配置：
    dev.py / stag.py / prod.py

辅助工具（config/tools/）：
    environment.py     - 环境检测（ENVIRONMENT, RUN_MODE, IS_CONTAINER_MODE）
    redis.py           - Redis 配置辅助函数
"""
```

---

### 3. config/defaults/apps.py — Django 核心

文件：[`{{cookiecutter.project_name}}/config/defaults/apps.py`](file:///config/defaults/apps.py)

```python
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
```

---

### 4. config/defaults/__init__.py — 功能模块汇总导入

文件：[`{{cookiecutter.project_name}}/config/defaults/__init__.py`](file:///config/defaults/__init__.py)

```python
"""功能模块汇总导入 — settings.py 第 2 步通过 `from config.defaults import *` 加载"""
# 加载顺序约束：apps 必须最先，env_override 必须最后

# 1. Django 核心（必须最先加载）
from config.defaults.apps import *  # noqa
# 2. 数据库
from config.defaults.database import *  # noqa
# 3. 缓存
from config.defaults.cache import *  # noqa
# 4. REST Framework
from config.defaults.rest_framework import *  # noqa
# 5. 静态资源
from config.defaults.static_files import *  # noqa
# 6. Session
from config.defaults.session import *  # noqa
# 7. 日志
from config.defaults.logging import *  # noqa

{% if cookiecutter.enable_celery == "yes" %}
# 8. Celery（条件生成）
from config.defaults.celery import *  # noqa
{% endif %}
{% if cookiecutter.enable_cors == "yes" %}
# 9. CORS（条件生成）
from config.defaults.cors import *  # noqa
{% endif %}
{% if cookiecutter.enable_i18n == "yes" %}
# 10. 国际化（条件生成）
from config.defaults.i18n import *  # noqa
{% endif %}
{% if cookiecutter.enable_api_docs == "yes" %}
# 11. API 文档（条件生成）
from config.defaults.api_docs import *  # noqa
{% endif %}

# 12. 环境变量覆盖（必须最后加载，可覆盖前面所有配置）
from config.defaults.env_override import *  # noqa
```

---

### 5. config/defaults/database.py — 数据库

文件：[`{{cookiecutter.project_name}}/config/defaults/database.py`](file:///config/defaults/database.py)

```python
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
```

---

### 6. config/defaults/cache.py — 缓存

文件：[`{{cookiecutter.project_name}}/config/defaults/cache.py`](file:///config/defaults/cache.py)

```python
"""缓存配置"""
from config.tools.redis import get_redis_cache_config

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "default-cache",
    },
    "db": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    },
}

{% if cookiecutter.enable_redis_cache == "yes" %}
# 若环境变量中配置了 Redis，则追加 Redis 缓存
_redis_config = get_redis_cache_config()
if _redis_config:
    CACHES["redis"] = _redis_config
{% endif %}
```

---

### 7. config/defaults/rest_framework.py — REST Framework

文件：[`{{cookiecutter.project_name}}/config/defaults/rest_framework.py`](file:///config/defaults/rest_framework.py)

```python
"""REST Framework + drf_resource 配置"""
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "drf_resource.response.renderers.CustomJSONRenderer",
    ],
    "DEFAULT_EXCEPTION_HANDLER": "drf_resource.exceptions.handlers.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# drf_resource 框架配置项
DRF_RESOURCE = {}

{% if cookiecutter.enable_api_docs == "yes" %}
# API 文档 schema class
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
{% endif %}
```

---

### 8. config/defaults/celery.py — Celery 默认配置（条件生成）

文件：[`{{cookiecutter.project_name}}/config/defaults/celery.py`](file:///config/defaults/celery.py)

```python
"""Celery 默认配置 — 仅 enable_celery=yes 时生成"""
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Shanghai"
CELERYD_CONCURRENCY = int(os.getenv("CELERYD_CONCURRENCY", 2))
```

---

### 9. config/defaults/cors.py — CORS（条件生成）

文件：[`{{cookiecutter.project_name}}/config/defaults/cors.py`](file:///config/defaults/cors.py)

```python
"""CORS 跨域配置 — 仅 enable_cors=yes 时生成"""
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

---

### 10. config/defaults/i18n.py — 国际化（条件生成）

文件：[`{{cookiecutter.project_name}}/config/defaults/i18n.py`](file:///config/defaults/i18n.py)

```python
"""国际化配置 — 仅 enable_i18n=yes 时生成"""
import os
from config import BASE_DIR

LANGUAGE_CODE = "zh-hans"
LANGUAGES = [
    ("zh-hans", "简体中文"),
    ("en", "English"),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]
USE_I18N = True
USE_L10N = True
```

---

### 11. config/defaults/api_docs.py — API 文档（条件生成）

文件：[`{{cookiecutter.project_name}}/config/defaults/api_docs.py`](file:///config/defaults/api_docs.py)

```python
"""API 文档配置 — 仅 enable_api_docs=yes 时生成"""
SPECTACULAR_SETTINGS = {
    "TITLE": "{{ cookiecutter.project_name }} API",
    "DESCRIPTION": "{{ cookiecutter.project_description }}",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}
```

---

### 12. config/defaults/static_files.py — 静态资源

文件：[`{{cookiecutter.project_name}}/config/defaults/static_files.py`](file:///config/defaults/static_files.py)

```python
"""静态资源配置"""
import os
from config import BASE_DIR, ENVIRONMENT

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

if ENVIRONMENT == "production":
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

---

### 13. config/defaults/session.py — Session

文件：[`{{cookiecutter.project_name}}/config/defaults/session.py`](file:///config/defaults/session.py)

```python
"""Session 配置"""
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60  # 7 天
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
```

---

### 14. config/defaults/logging.py — 日志

文件：[`{{cookiecutter.project_name}}/config/defaults/logging.py`](file:///config/defaults/logging.py)

```python
"""日志配置 — 自适应：开发/容器用 console，生产用 file + console"""
import os
from config import ENVIRONMENT, BASE_DIR, PROJECT_ROOT
from config.tools.environment import IS_CONTAINER_MODE

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")

_formatters = {
    "verbose": {
        "format": "[{asctime}] {levelname} {name} {message}",
        "style": "{",
    },
}

if ENVIRONMENT == "production" and not IS_CONTAINER_MODE:
    # 生产环境（非容器）：文件 + console
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(PROJECT_ROOT, "logs", "{{ cookiecutter.project_name }}.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "formatter": "verbose",
            },
        },
        "root": {"handlers": ["console", "file"], "level": LOG_LEVEL},
        "loggers": {
            "django": {"handlers": ["console", "file"], "level": LOG_LEVEL, "propagate": False},
            "drf_resource": {"handlers": ["console", "file"], "level": LOG_LEVEL, "propagate": False},
        },
    }
else:
    # 开发/容器环境：仅 console
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {"handlers": ["console"], "level": LOG_LEVEL},
        "loggers": {
            "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
            "drf_resource": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        },
    }
```

---

### 15. config/defaults/env_override.py — 环境变量覆盖

文件：[`{{cookiecutter.project_name}}/config/defaults/env_override.py`](file:///config/defaults/env_override.py)

```python
"""环境变量自动覆盖机制

SETTINGS_ 前缀的环境变量自动注入为 Django settings。
例如: SETTINGS_DEBUG=true → DEBUG=True
     SETTINGS_SECRET_KEY=xxx → SECRET_KEY=xxx

类型自动转换：true/false/none/int/str
"""
import os

_prefix = "SETTINGS_"
for _key, _value in os.environ.items():
    if _key.startswith(_prefix):
        _setting_name = _key[len(_prefix):]
        _lower = _value.lower()
        if _lower in ("true", "1", "yes"):
            _typed_value = True
        elif _lower in ("false", "0", "no"):
            _typed_value = False
        elif _lower in ("none", "null"):
            _typed_value = None
        else:
            try:
                _typed_value = int(_value)
            except ValueError:
                _typed_value = _value
        locals()[_setting_name] = _typed_value
```

---

### 16. config/role/web.py — Web 角色

文件：[`{{cookiecutter.project_name}}/config/role/web.py`](file:///config/role/web.py)

```python
"""
Web 角色配置
启动方式: DJANGO_ROLE=web python manage.py runserver
"""
import os
from config import ENVIRONMENT

# Web 角色不需要额外修改 INSTALLED_APPS 和 MIDDLEWARE，
# config/defaults/apps.py 中的配置即为 Web 角色的默认配置。

# 开发环境特定覆盖
if ENVIRONMENT == "development":
    DEBUG = True
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

{% if cookiecutter.enable_redis_cache == "yes" %}
# 生产环境 Session 使用 Redis（通过环境变量检测，避免跨模块引用 CACHES）
if ENVIRONMENT == "production" and os.getenv("REDIS_HOST"):
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "redis"
{% endif %}
```

---

### 17. config/role/worker.py — Worker 角色

文件：[`{{cookiecutter.project_name}}/config/role/worker.py`](file:///config/role/worker.py)

```python
"""
Worker 角色配置
启动方式: DJANGO_ROLE=worker celery -A {{ cookiecutter.project_name }} worker -l info
"""
import os

{% if cookiecutter.enable_celery == "yes" %}
# Worker 角色仅需要 Celery + 核心模块，不需要 REST Framework / CORS / API 文档
ROOT_URLCONF = "{{ cookiecutter.project_name }}.urls"

# 精简 INSTALLED_APPS：移除 drf_resource、drf_spectacular 等 Web 专属 App
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    {% if cookiecutter.enable_celery == "yes" %}
    "django_celery_beat",
    "django_celery_results",
    {% endif %}
    "{{ cookiecutter.project_name }}.apps.example",
]

# Worker 不需要 MIDDLEWARE
MIDDLEWARE = []

# 禁用 DRF
REST_FRAMEWORK = {}

# Celery 配置（从环境变量读取，生产环境强制）
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = False
CELERYD_CONCURRENCY = int(os.getenv("CELERYD_CONCURRENCY", 2))
{% endif %}

# 定时任务调度表（参考 bk-monitor 的 DEFAULT_CRONTAB 模式）
# 格式: (task_module, cron_schedule, run_type)
# run_type: "global" 全局执行 / "cluster" 分集群执行
DEFAULT_CRONTAB = [
    # 示例：
    # ("{{ cookiecutter.project_name }}.apps.example.tasks.cleanup_expired_data", "*/30 * * * *", "global"),
]

# 耗时任务单独队列
LONG_TASK_CRONTAB = []

# 排除特定任务
EXCLUDE_WORKER_TASKS = []
```

---

### 18. config/{dev,stag,prod}.py — 环境差异

#### config/dev.py

文件：[`{{cookiecutter.project_name}}/config/dev.py`](file:///config/dev.py)

```python
"""开发环境配置"""
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 开发环境使用简单静态资源
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

{% if cookiecutter.enable_celery == "yes" %}
# 开发环境 Celery 同步执行（调试用）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
{% endif %}
```

#### config/stag.py

文件：[`{{cookiecutter.project_name}}/config/stag.py`](file:///config/stag.py)

```python
"""测试环境配置"""
DEBUG = False
ALLOWED_HOSTS = ["*"]
```

#### config/prod.py

文件：[`{{cookiecutter.project_name}}/config/prod.py`](file:///config/prod.py)

```python
"""生产环境配置"""
import os

DEBUG = False
ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "").split(",")
    if os.getenv("ALLOWED_HOSTS")
    else []
)

{% if cookiecutter.enable_redis_cache == "yes" %}
# 生产环境 Session 使用 Redis（通过环境变量检测）
if os.getenv("REDIS_HOST"):
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "redis"
{% endif %}

{% if cookiecutter.enable_celery == "yes" %}
# 生产环境 Celery 配置
CELERY_TASK_ALWAYS_EAGER = False
CELERYD_CONCURRENCY = int(os.getenv("CELERYD_CONCURRENCY", 4))
{% endif %}
```

---

### 19. {{cookiecutter.project_name}}/settings.py — 入口

文件：[`{{cookiecutter.project_name}}/settings.py`](file:///settings.py)

```python
"""
Django settings 入口

加载顺序（6 步）：
    1. config/__init__.py  → 基础常量
    2. config/defaults/     → 功能模块
    3. config/role/{role}.py → 角色差异
    4. config/{env}.py      → 环境差异
    5. 环境变量覆盖          → SETTINGS_ 前缀自动注入
    6. local_settings.py    → 开发环境个人覆盖
"""
import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
DJANGO_ROLE = os.getenv("DJANGO_ROLE", "web")

ENV_MODULE_MAP = {
    "development": "dev",
    "testing": "stag",
    "production": "prod",
}

# 1. 基础常量
from config import *  # noqa

# 2. 功能模块
from config.defaults import *  # noqa

# 3. 角色差异
_role_module = f"config.role.{DJANGO_ROLE}"
try:
    _role = __import__(_role_module, globals(), locals(), ["*"])
    for _s in dir(_role):
        if _s.isupper():
            locals()[_s] = getattr(_role, _s)
except ImportError:
    raise ImportError(f"无法导入角色配置 '{_role_module}'，请检查 DJANGO_ROLE 环境变量")

# 4. 环境差异
_env = ENV_MODULE_MAP.get(DJANGO_ENV, "dev")
_env_module = f"config.{_env}"
try:
    _module = __import__(_env_module, globals(), locals(), ["*"])
    for _s in dir(_module):
        if _s.isupper():
            locals()[_s] = getattr(_module, _s)
except ImportError as e:
    raise ImportError(f"无法导入环境配置 '{_env_module}': {e}")

# 5. 环境变量覆盖（config/defaults/env_override.py 已加载，此处省略）

# 6. local_settings.py 覆盖
if DJANGO_ENV == "development":
    try:
        from local_settings import *  # noqa
    except ImportError:
        pass

{% if cookiecutter.database_backend == "mysql" %}
# MySQL 兼容（Django 4.2+）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
{% endif %}
```

---

### 20. config/tools/environment.py

```python
"""环境检测工具"""
import os

__all__ = ["ENVIRONMENT", "RUN_MODE", "IS_CONTAINER_MODE"]

ENVIRONMENT = os.getenv("DJANGO_ENV", "development")
RUN_MODE = {
    "development": "DEVELOP",
    "testing": "TEST",
    "production": "PRODUCT",
}.get(ENVIRONMENT, "DEVELOP")
IS_CONTAINER_MODE = os.getenv("DEPLOY_MODE") == "kubernetes" or os.path.exists("/.dockerenv")
```

### 21. config/tools/redis.py

```python
"""Redis 配置辅助"""
import os

def get_redis_url(db: int = 0) -> str:
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    password = os.getenv("REDIS_PASSWORD", "")
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"

def get_redis_cache_config() -> dict | None:
    host = os.getenv("REDIS_HOST")
    port = os.getenv("REDIS_PORT")
    if not host or not port:
        return None
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": get_redis_url(1),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
```

## 异常处理

| 场景 | 行为 | 对外暴露 |
|------|------|---------|
| Redis 未配置但 enable_redis_cache=yes | `get_redis_cache_config()` 返回 None，fallback LocMem | 否，静默 |
| DJANGO_ROLE 设置为不存在的角色 | ImportError: 无法导入角色配置 | 是，控制台 |
| MySQL 驱动未安装 | try/except 跳过 | 否 |

---

## 补充：config/celery/ 包（条件生成）

仅当 `enable_celery=yes` 时生成。参考 bk-monitor 的 `config/celery/` 包结构。

### config/celery/__init__.py

```python
"""Celery app 包"""
```

### config/celery/celery.py — Celery app 初始化

文件：[`{{cookiecutter.project_name}}/config/celery/celery.py`](file:///config/celery/celery.py)

```python
"""Celery app + autodiscover + signals"""
import os

from celery import Celery, platforms
from celery.signals import beat_init, setup_logging
from django.conf import settings
from django.db import close_old_connections

# 允许 root 启动 celery
platforms.C_FORCE_ROOT = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ cookiecutter.project_name }}.settings")

app = Celery("{{ cookiecutter.project_name }}")

# 从 config.celery.config 加载配置
app.config_from_object("config.celery.config:Config")

# 自动发现所有 INSTALLED_APPS 中的 tasks.py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f"Request: {self.request!r}")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """使用 Django 的 LOGGING 配置 Celery 日志"""
    from logging.config import dictConfig
    dictConfig(settings.LOGGING)


@beat_init.connect
def clean_db_connections(sender, **kwargs):
    """beat 启动时清理旧 DB 连接"""
    close_old_connections()
```

**借鉴 bk-monitor 的优化**：
- `C_FORCE_ROOT = True` — 允许 root 用户启动 Celery
- `setup_logging` 信号 — 让 Celery 使用 Django 的 LOGGING 配置
- `beat_init` 信号 — beat 启动时清理 DB 连接，避免连接泄漏
- `autodiscover_tasks` — 自动发现所有 App 的 tasks.py

### config/celery/config.py — Celery Config 类

文件：[`{{cookiecutter.project_name}}/config/celery/config.py`](file:///config/celery/config.py)

```python
"""Celery 配置类 + beat_schedule"""
from celery.schedules import crontab
from django.conf import settings


class Config:
    """Celery 配置"""
    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND

    # 使用 django_celery_beat 的调度器
    beat_scheduler = "django_celery_beat.schedulers.DatabaseScheduler"

    # 序列化
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]

    # 如果是 Web 角色，Celery 任务同步执行（调试用）
    task_always_eager = settings.DJANGO_ROLE != "worker" if hasattr(settings, "DJANGO_ROLE") else False

    # 时区
    timezone = "Asia/Shanghai"

    # 定时任务调度（从 DEFAULT_CRONTAB 动态构建）
    beat_schedule = {}
    # 用户可在 role/worker.py 的 DEFAULT_CRONTAB 中添加定时任务
    # 也可在此直接配置 beat_schedule
```

**与 bk-monitor 的差异**：
- bk-monitor 使用 `pickle` 序列化，模板默认 `json`（更安全、跨语言兼容）
- bk-monitor 的 `beat_schedule` 硬编码了 20+ 个监控任务，模板留空供用户填充
- bk-monitor 使用自定义 `MonitorDatabaseScheduler`，模板使用标准的 `DatabaseScheduler`

---

## 补充：config/tools/mysql.py（条件生成）

仅当 `database_backend=mysql` 时生成。参考 bk-monitor 的多环境变量 fallback 模式。

```python
"""MySQL 配置辅助 - 多环境变量 fallback"""
import os


def get_mysql_settings() -> tuple:
    """
    从环境变量获取 MySQL 连接配置
    支持多个环境变量名 fallback，适配不同部署环境
    """
    name = os.getenv("DB_NAME") or os.getenv("MYSQL_NAME", "{{ cookiecutter.project_name }}")
    user = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
    password = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306"))
    return name, host, port, user, password
```

**借鉴 bk-monitor 的模式**：
- bk-monitor 的 `mysql.py` 支持多个环境变量名 fallback（`DB_*` / `MYSQL_*` / `BKAPP_*`），适配 PaaS V2/V3
- 模板精简为 `DB_*` / `MYSQL_*` 两组 fallback，覆盖常见部署场景
