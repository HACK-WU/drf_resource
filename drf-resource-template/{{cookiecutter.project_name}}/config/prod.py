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
