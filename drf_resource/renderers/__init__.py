"""
DRF-Resource 统一渲染器模块

提供统一的响应格式化和渲染功能，与异常处理器配合使用，
确保 API 响应格式的一致性。

配置方式:
    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': [
            'drf_resource.renderers.ResourceJSONRenderer',
        ],
    }
"""

from .base import ResponseFormatter, default_response_formatter
from .json_renderer import ResourceJSONRenderer

__all__ = [
    # 渲染器
    "ResourceJSONRenderer",
    # 格式化器
    "ResponseFormatter",
    "default_response_formatter",
]
