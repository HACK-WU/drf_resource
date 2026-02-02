"""
DRF-Resource 响应格式化器

提供统一的响应格式化功能，与 ExceptionResponseFormatter 配合使用，
确保成功响应和异常响应的格式一致。

默认响应格式：
    {
        "result": true,
        "code": 0,
        "message": "success",
        "data": { ... }
    }
"""

from typing import Any

from drf_resource.response.formatter import BaseResponseFormatter


class ResponseFormatter(BaseResponseFormatter):
    """
    响应格式化器

    继承自 BaseResponseFormatter，用于格式化成功响应，
    与异常处理器中的 ExceptionResponseFormatter 配合使用，
    确保 API 响应格式的统一性。

    默认格式：
    {
        "result": true,
        "code": 200,
        "message": "success",
        "data": { ... }
    }

    可通过继承此类来自定义响应格式。

    Example:
        class CustomFormatter(ResponseFormatter):
            def format(self, data: Any, **kwargs) -> dict:
                return {
                    "success": True,
                    "payload": data,
                    "meta": kwargs.get("meta", {}),
                }

        # 在渲染器中使用
        renderer = ResourceJSONRenderer(formatter=CustomFormatter())
    """

    def format(self, data: Any, **kwargs) -> dict:
        """
        格式化成功响应

        Args:
            data: 原始响应数据
            **kwargs: 额外的上下文参数，可包含：
                - message: 自定义成功消息
                - code: 自定义成功码
                - meta: 元数据信息

        Returns:
            格式化后的响应字典
        """
        return self.format_success(
            data=data,
            code=kwargs.get("code"),
            message=kwargs.get("message"),
        )

    def is_formatted(self, data: Any) -> bool:
        """
        检查数据是否已经是格式化后的响应

        避免重复包装已经格式化的响应数据。

        Args:
            data: 待检查的数据

        Returns:
            True 表示已格式化，False 表示未格式化
        """
        if not isinstance(data, dict):
            return False

        # 检查是否包含标准响应字段
        required_fields = {"result", "code", "message", "data"}
        if not required_fields.issubset(data.keys()):
            return False

        # 检查字段类型是否正确
        return isinstance(data.get("result"), bool) and isinstance(
            data.get("code"), int
        )

    def should_format(self, data: Any, **kwargs) -> bool:
        """
        判断是否应该格式化响应

        可以通过继承重写此方法来实现自定义的判断逻辑。

        Args:
            data: 原始响应数据
            **kwargs: 额外的上下文参数，可包含：
                - skip_format: 显式跳过格式化

        Returns:
            True 表示应该格式化，False 表示跳过格式化
        """
        # 显式指定跳过格式化
        if kwargs.get("skip_format", False):
            return False

        # 已经格式化的数据不再重复格式化
        if self.is_formatted(data):
            return False

        return True


# 默认格式化器实例
default_response_formatter = ResponseFormatter()
