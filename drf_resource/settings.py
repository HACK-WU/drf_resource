from django.conf import settings
from rest_framework.settings import APISettings

# 核心配置
DEFAULT = {
    # 缓存配置
    "DEFAULT_USING_CACHE": "drf_resource.cache.DefaultUsingCache",
    # 自动发现配置
    "AUTO_DISCOVERY": True,
    "RESOURCE_DATA_COLLECT_ENABLED": False,
    "RESOURCE_DATA_COLLECT_RATIO": 0.1,
    # 认证配置
    "USERNAME_FIELD": "username",
    "DEFAULT_USERNAME": "system",
    # HTTP Resource 配置
    "HTTP_AUTH_ENABLED": False,
    "HTTP_AUTH_HEADER": "Authorization",
    "HTTP_AUTH_PARAMS": {},
    "HTTP_STANDARD_FORMAT": True,
    "HTTP_TIMEOUT": 60,
    "HTTP_VERIFY_SSL": True,
    # Celery 配置
    "CELERY_QUEUE": "celery_resource",
    # OpenTelemetry 配置
    "OPENTELEMETRY_ENABLED": False,
    # API 文档配置
    "ENABLE_API_DOCS": True,  # 是否启用 API 文档（drf-spectacular）
    "SCHEMA_CACHE_TIMEOUT": 3600,  # Schema 缓存超时时间（秒），默认 1 小时。设为 0 禁用缓存
    "DOCS_TAG_THRESHOLD": 100,  # 分组接口数量警告阈值，超过此数量会显示警告提示
    "DOCS_PATH_PREFIX_GROUPING_ENABLED": True,  # 是否启用路径前缀二级分组功能
    "DOCS_PATH_PREFIX_THRESHOLD": 50,  # 启用路径前缀分组的API数量阈值，超过此数量才启用分组
}

# 配置项列表（包含向后兼容配置）
IMPORT_STRINGS = [
    # 核心配置
    "DEFAULT_USING_CACHE",
    "AUTO_DISCOVERY",
    "RESOURCE_DATA_COLLECT_ENABLED",
    "RESOURCE_DATA_COLLECT_RATIO",
    "USERNAME_FIELD",
    "DEFAULT_USERNAME",
    # HTTP Resource 配置
    "HTTP_AUTH_ENABLED",
    "HTTP_AUTH_HEADER",
    "HTTP_AUTH_PARAMS",
    "HTTP_STANDARD_FORMAT",
    "HTTP_TIMEOUT",
    "HTTP_VERIFY_SSL",
    # Celery 配置
    "CELERY_QUEUE",
    # OpenTelemetry 配置
    "OPENTELEMETRY_ENABLED",
    # API 文档配置
    "ENABLE_API_DOCS",
]


class DrfResourceSettings(APISettings):
    """
    DrfResource Settings
    支持从 Django settings 读取 DRF_RESOURCE 配置，
    并提供向后兼容的降级机制。
    """

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "DRF_RESOURCE", {})
        return self._user_settings


resource_settings = DrfResourceSettings(None, DEFAULT, IMPORT_STRINGS)
