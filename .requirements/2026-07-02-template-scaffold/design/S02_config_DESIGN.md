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

### 4–14. 其余 defaults/ 模块

| 文件 | 关键代码摘要 |
|------|------------|
| `database.py` | 根据 `database_backend` 变量生成 sqlite/mysql/postgresql 的 DATABASES 配置 |
| `cache.py` | LocMem + DB Cache；若 `enable_redis_cache` 则追加 Redis（从环境变量构建） |
| `rest_framework.py` | 集成 drf_resource 的 CustomJSONRenderer + custom_exception_handler |
| `celery.py` | `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND`，仅 `enable_celery=yes` 生成 |
| `cors.py` | `CORS_ALLOW_ALL_ORIGINS = True`，仅 `enable_cors=yes` 生成 |
| `i18n.py` | `LANGUAGE_CODE = "zh-hans"`, `LOCALE_PATHS`，仅 `enable_i18n=yes` 生成 |
| `api_docs.py` | `SPECTACULAR_SETTINGS`，设置 `REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"]`，仅 `enable_api_docs=yes` 生成 |
| `static_files.py` | whitenoise `CompressedManifestStaticFilesStorage` |
| `session.py` | `SESSION_COOKIE_AGE = 7天`, `SESSION_ENGINE = db` |
| `logging.py` | 自适应：容器/开发 → console 日志；生产 → file + console |
| `env_override.py` | `SETTINGS_` 前缀环境变量自动注入 |

> 完整代码参见原单文档 DESIGN.md（已删除），后续 design-to-code 时补全。

---

### 15. config/role/web.py — Web 角色（新增）

文件：[`{{cookiecutter.project_name}}/config/role/web.py`](file:///config/role/web.py)

```python
"""
Web 角色配置
启动方式: DJANGO_ROLE=web python manage.py runserver
"""
from config import ENVIRONMENT

# 使用 config/overview.py 中定义的完整加载顺序

# Web 角色不需要额外修改 INSTALLED_APPS 和 MIDDLEWARE，
# config/defaults/apps.py 中的配置即为 Web 角色的默认配置。

# 开发环境特定覆盖
if ENVIRONMENT == "development":
    DEBUG = True
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 生产环境 Session 使用 Redis（若启用）
{% if cookiecutter.enable_redis_cache == "yes" %}
if ENVIRONMENT == "production" and "redis" in CACHES:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "redis"
{% endif %}
```

---

### 16. config/role/worker.py — Worker 角色（新增）

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
```

---

### 17. config/{dev,stag,prod}.py — 环境差异

| 文件 | DEBUG | 关键覆盖 |
|------|-------|---------|
| `dev.py` | True | 简化静态资源，支持 local_settings.py |
| `stag.py` | False | — |
| `prod.py` | False | ALLOWED_HOSTS 从环境变量，Redis Session，Celery 并发数 |

---

### 18. {{cookiecutter.project_name}}/settings.py — 入口

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
        if _s == _s.upper():
            locals()[_s] = getattr(_role, _s)
except ImportError:
    raise ImportError(f"无法导入角色配置 '{_role_module}'，请检查 DJANGO_ROLE 环境变量")

# 4. 环境差异
_env = ENV_MODULE_MAP.get(DJANGO_ENV, "dev")
_env_module = f"config.{_env}"
try:
    _module = __import__(_env_module, globals(), locals(), ["*"])
    for _s in dir(_module):
        if _s == _s.upper():
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

### 19. config/tools/environment.py

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

### 20. config/tools/redis.py

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
