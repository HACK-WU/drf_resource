"""
DRF-Resource 响应模块

提供统一的响应格式化和渲染功能，与异常处理器配合使用，
确保 API 响应格式的一致性。

包含:
    - BaseResponseFormatter: 响应格式化器基类
    - ResponseFormatter: 成功响应格式化器
    - ResourceJSONRenderer: JSON 渲染器
    - ResourceJSONEncoder: JSON 编码器

配置方式:
    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': [
            'drf_resource.response.ResourceJSONRenderer',
        ],
    }
"""

from drf_resource.response.formatter import BaseResponseFormatter
from drf_resource.response.response_formatter import (
    ResponseFormatter,
    default_response_formatter,
)
from drf_resource.response.renderers import (
    ResourceJSONRenderer,
    ResourceJSONEncoder,
    get_renderer,
)

__all__ = [
    # 基础格式化器
    "BaseResponseFormatter",
    # 响应格式化器
    "ResponseFormatter",
    "default_response_formatter",
    # 渲染器
    "ResourceJSONRenderer",
    "ResourceJSONEncoder",
    "get_renderer",
]
