"""缓存配置"""
{% if cookiecutter.enable_redis_cache == "yes" %}
from config.tools.redis import get_redis_cache_config
{% endif %}

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
