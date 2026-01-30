"""
DRF-Resource 异常处理器

提供统一的 DRF 异常处理和响应格式化功能。

配置方式:
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'drf_resource.exceptions.handlers.resource_exception_handler'
    }
"""

import logging
from typing import Any

from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from drf_resource.response import BaseResponseFormatter

from .base import ResourceException
from .codes import StandardErrorCodes

logger = logging.getLogger(__name__)


class ExceptionResponseFormatter(BaseResponseFormatter):
    """
    异常响应格式化器

    继承自 BaseResponseFormatter，用于格式化异常响应。

    默认格式：
    {
        "result": false,
        "code": 1000,
        "message": "Error message",
        "data": null,
        "error": { ... }
    }

    可通过继承此类来自定义响应格式。

    Example:
        class CustomFormatter(ExceptionResponseFormatter):
            def format(self, exc: Exception, context: dict) -> dict:
                if isinstance(exc, ResourceException):
                    return {
                        "success": False,
                        "error_code": exc.code,
                        "error_message": exc.message,
                    }
                return super().format(exc, context)
    """

    def format(self, exc: Exception, context: dict) -> dict:
        """
        格式化异常响应（统一入口）

        Args:
            exc: 异常实例
            context: DRF 提供的上下文信息

        Returns:
            格式化后的响应字典
        """
        if isinstance(exc, ResourceException):
            return exc.to_dict()

        error_code = self._get_error_code(exc)
        message = self._get_error_message(exc)
        data = self._get_error_data(exc)

        error_detail = self.build_error_detail(
            error_type=exc.__class__.__name__,
            code=error_code,
            message=message,
        )
        return self.format_error(
            code=error_code,
            message=message,
            data=data,
            error=error_detail,
        )

    def _get_error_code(self, exc: Exception) -> int:
        """
        从异常中获取错误码

        优先级：
        1. exc.code 属性
        2. exc.error_code 属性
        3. 根据异常类型映射（Http404 -> NOT_FOUND, APIException -> VALIDATION_ERROR）
        4. 默认 INTERNAL_ERROR

        Args:
            exc: 异常实例

        Returns:
            错误码
        """
        # 优先使用 code 属性
        if hasattr(exc, "code") and isinstance(exc.code, int):
            return exc.code

        # 其次使用 error_code 属性
        if hasattr(exc, "error_code") and isinstance(exc.error_code, int):
            return exc.error_code

        # 根据异常类型映射错误码
        if isinstance(exc, Http404):
            return StandardErrorCodes.NOT_FOUND.code

        if isinstance(exc, APIException):
            return StandardErrorCodes.VALIDATION_ERROR.code

        # 默认返回内部错误码
        return StandardErrorCodes.INTERNAL_ERROR.code

    def _get_error_message(self, exc: Exception) -> str:
        """
        从异常中获取错误消息

        Args:
            exc: 异常实例

        Returns:
            错误消息
        """
        if isinstance(exc, Http404):
            return "Resource not found"

        if isinstance(exc, APIException):
            return _extract_drf_error_detail(exc.detail)

        return str(exc) if str(exc) else "Internal server error"

    def _get_error_data(self, exc: Exception) -> Any:
        """
        从异常中获取附加数据

        Args:
            exc: 异常实例

        Returns:
            附加数据，如果没有则返回 None
        """
        # 优先使用自定义异常的 data 属性
        if hasattr(exc, "data"):
            return exc.data

        # DRF 异常包含 detail 作为附加数据
        if isinstance(exc, APIException):
            return exc.detail

        return None


# 默认格式化器实例
default_formatter = ExceptionResponseFormatter()


def _extract_drf_error_detail(detail: Any) -> str:
    """
    从 DRF 错误详情中提取字符串消息

    DRF 的 detail 可能是字符串、字典或列表的嵌套结构，
    此函数递归提取第一个有效的错误消息。

    Args:
        detail: DRF 异常的 detail 属性

    Returns:
        提取的错误消息字符串
    """
    if isinstance(detail, str):
        return detail
    elif isinstance(detail, dict):
        for key, value in detail.items():
            if value:
                inner = _extract_drf_error_detail(value)
                return f"({key}) {inner}"
        return ""
    elif isinstance(detail, list):
        for item in detail:
            if item:
                return _extract_drf_error_detail(item)
        return ""
    # 处理 DRF 的 ErrorDetail 对象
    elif hasattr(detail, "__str__"):
        return str(detail)
    return "Validation error"


def resource_exception_handler(
    exc: Exception, context: dict, formatter: ExceptionResponseFormatter | None = None
) -> Response | None:
    """
    DRF-Resource 统一异常处理器

    处理以下类型的异常：
    1. ResourceException 及其子类 - 框架自定义异常
    2. DRF APIException - DRF 内置异常（验证错误等）
    3. Django Http404 - 404 错误
    4. 其他未知异常 - 转换为 500 错误

    配置方式:
        在 Django settings.py 中配置:
        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': 'drf_resource.exceptions.handlers.resource_exception_handler'
        }

    自定义格式化器:
        def custom_handler(exc, context):
            return resource_exception_handler(exc, context, formatter=CustomFormatter())

    Args:
        exc: 异常实例
        context: DRF 提供的上下文，包含 view, args, kwargs, request 等
        formatter: 可选的自定义格式化器

    Returns:
        Response 对象，或 None（让 DRF 继续处理）
    """
    formatter = formatter or default_formatter

    # 处理框架异常
    if isinstance(exc, ResourceException):
        exc.log()
        return Response(formatter.format(exc, context), status=exc.http_status)

    # 处理 DRF 内置异常
    if isinstance(exc, APIException):
        return Response(formatter.format(exc, context), status=exc.status_code)

    # 处理 Django 404
    if isinstance(exc, Http404):
        return Response(
            formatter.format(exc, context), status=status.HTTP_404_NOT_FOUND
        )

    # 未知异常 - 记录日志并返回 500
    logger.exception("Unhandled exception: %s", exc)
    return Response(
        formatter.format(exc, context), status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def get_exception_handler(formatter: ExceptionResponseFormatter | None = None):
    """
    获取异常处理器的工厂函数

    用于需要自定义格式化器但又想保持配置简洁的场景。

    Example:
        # settings.py
        from drf_resource.common_errors.exceptions .handlers import get_exception_handler, ExceptionResponseFormatter

        class MyFormatter(ExceptionResponseFormatter):
            pass

        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': get_exception_handler(MyFormatter())
        }

    Args:
        formatter: 自定义格式化器实例

    Returns:
        配置好格式化器的异常处理函数
    """

    def handler(exc: Exception, context: dict) -> Response | None:
        return resource_exception_handler(exc, context, formatter=formatter)

    return handler
