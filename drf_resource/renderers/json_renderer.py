"""
DRF-Resource JSON 渲染器

提供统一的 JSON 响应渲染功能，自动将响应数据包装为标准格式。

配置方式:
    REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': [
            'drf_resource.renderers.ResourceJSONRenderer',
        ],
    }
"""

import datetime
import decimal
import json
import uuid
from typing import Any

from rest_framework.renderers import JSONRenderer

from .base import ResponseFormatter, default_response_formatter


class ResourceJSONEncoder(json.JSONEncoder):
    """
    扩展的 JSON 编码器

    支持更多 Python 类型的序列化：
    - datetime/date/time
    - Decimal
    - UUID
    - bytes
    - set/frozenset
    - 自定义对象（通过 to_dict/to_json 方法）
    """

    def default(self, obj: Any) -> Any:
        """
        处理默认 JSON 编码器不支持的类型

        Args:
            obj: 待序列化的对象

        Returns:
            可序列化的值
        """
        # 日期时间类型
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, datetime.time):
            return obj.isoformat()

        # Decimal 类型
        if isinstance(obj, decimal.Decimal):
            return float(obj)

        # UUID 类型
        if isinstance(obj, uuid.UUID):
            return str(obj)

        # bytes 类型 - 优先尝试 UTF-8 解码，失败则使用 base64
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except UnicodeDecodeError:
                # 使用 base64 编码处理无法解码的二进制数据
                try:
                    import base64

                    return base64.b64encode(obj).decode("ascii")
                except Exception:
                    # 极端情况下的兜底处理：返回十六进制表示
                    return obj.hex()

        # set/frozenset 类型
        if isinstance(obj, set | frozenset):
            return list(obj)

        # 支持自定义序列化方法
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "to_json"):
            return obj.to_json()

        # 回退到默认行为
        return super().default(obj)


class ResourceJSONRenderer(JSONRenderer):
    """
    统一 JSON 渲染器

    自动将响应数据包装为标准格式：
    {
        "result": true,
        "code": 0,
        "message": "success",
        "data": { ... }
    }

    特性：
    - 自动包装响应为标准格式
    - 跳过已格式化的响应（避免重复包装）
    - 支持自定义格式化器
    - 扩展的 JSON 类型支持

    配置方式:
        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': [
                'drf_resource.renderers.ResourceJSONRenderer',
            ],
        }

    自定义格式化器:
        # 推荐方式：通过子类覆盖类属性
        class CustomFormatter(ResponseFormatter):
            def format(self, data, **kwargs):
                return {"success": True, "payload": data}

        class CustomRenderer(ResourceJSONRenderer):
            formatter = CustomFormatter()

        # 不推荐：实例化时传参（在某些场景下可能不生效）
        # renderer = ResourceJSONRenderer(formatter=CustomFormatter())

    跳过格式化:
        # 在 Response 中设置
        return Response(data, headers={"X-Skip-Format": "true"})

        # 或者返回已格式化的数据
        return Response({"result": True, "code": 0, "message": "ok", "data": data})

    Example:
        # views.py
        class MyView(APIView):
            renderer_classes = [ResourceJSONRenderer]

            def get(self, request):
                # 返回原始数据，渲染器会自动包装
                return Response({"items": [1, 2, 3]})

        # 响应结果：
        # {
        #     "result": true,
        #     "code": 0,
        #     "message": "success",
        #     "data": {"items": [1, 2, 3]}
        # }
    """

    # 使用自定义 JSON 编码器
    encoder_class = ResourceJSONEncoder

    # 默认格式化器（可在子类中覆盖）
    formatter: ResponseFormatter = default_response_formatter

    # 用于跳过格式化的响应头
    SKIP_FORMAT_HEADER = "X-Skip-Format"

    def __init__(self, formatter: ResponseFormatter | None = None, **kwargs):
        """
        初始化渲染器

        Args:
            formatter: 自定义响应格式化器
            **kwargs: 其他参数传递给父类
        """
        super().__init__(**kwargs)
        if formatter is not None:
            self.formatter = formatter

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict | None = None,
    ) -> bytes:
        """
        渲染响应数据

        自动将数据包装为标准响应格式，除非：
        1. 数据已经是标准格式
        2. 响应头指示跳过格式化
        3. 响应状态码表示错误（由异常处理器处理）

        Args:
            data: 原始响应数据
            accepted_media_type: 接受的媒体类型
            renderer_context: 渲染上下文，包含 view, request, response 等

        Returns:
            序列化后的 JSON 字节串
        """
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        # 判断是否应该格式化
        should_format = self._should_format(data, response, renderer_context)

        if should_format:
            data = self.formatter.format(data)

        return super().render(data, accepted_media_type, renderer_context)

    def _should_format(self, data: Any, response: Any, renderer_context: dict) -> bool:
        """
        判断是否应该格式化响应

        Args:
            data: 响应数据
            response: Response 对象
            renderer_context: 渲染上下文

        Returns:
            True 表示应该格式化，False 表示跳过
        """
        # 空数据不格式化
        if data is None:
            return False

        # 检查响应头是否指示跳过格式化
        if response is not None:
            skip_header = response.get(self.SKIP_FORMAT_HEADER, "").lower()
            if skip_header in ("true", "1", "yes"):
                return False

            # 错误响应不格式化（由异常处理器处理）
            if response.status_code >= 400:
                return False

        # 使用格式化器的判断逻辑
        return self.formatter.should_format(data)


def get_renderer(formatter: ResponseFormatter | None = None) -> type:
    """
    获取配置了自定义格式化器的渲染器类

    用于需要自定义格式化器但又想保持配置简洁的场景。

    Example:
        # settings.py
        from drf_resource.renderers import get_renderer, ResponseFormatter

        class MyFormatter(ResponseFormatter):
            SUCCESS_MESSAGE = "OK"

        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': [
                get_renderer(MyFormatter()),
            ]
        }

    Args:
        formatter: 自定义格式化器实例

    Returns:
        配置好格式化器的渲染器类
    """
    if formatter is None:
        return ResourceJSONRenderer

    class ConfiguredRenderer(ResourceJSONRenderer):
        pass

    ConfiguredRenderer.formatter = formatter
    return ConfiguredRenderer
