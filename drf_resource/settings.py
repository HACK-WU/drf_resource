"""
DRF Resource - Django REST Framework 资源化框架
Copyright (C) 2024-2025

Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
