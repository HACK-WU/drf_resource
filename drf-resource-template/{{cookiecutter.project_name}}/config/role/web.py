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
