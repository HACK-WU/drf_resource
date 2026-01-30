"""
DRF-Resource 统一响应格式化器基类

提供统一的响应格式定义，确保成功响应和异常响应的结构一致。
ResponseFormatter 和 ExceptionResponseFormatter 都继承自此基类。

标准响应格式：
    成功响应：
    {
        "result": true,
        "code": 0,
        "message": "success",
        "data": { ... }
    }

    异常响应：
    {
        "result": false,
        "code": 1000,
        "message": "Error message",
        "data": null,
        "error": {
            "type": "ErrorType",
            "code": 1000,
            "message": "Error message"
        }
    }
"""

from typing import Any


class BaseResponseFormatter:
    """
    响应格式化器基类

    定义统一的响应结构，确保整个框架的响应格式一致性。
    所有格式化器都应继承此类以保持格式统一。

    Attributes:
        SUCCESS_CODE: 默认成功码
        SUCCESS_MESSAGE: 默认成功消息

    Example:
        class CustomFormatter(BaseResponseFormatter):
            def format_success(self, data: Any, code: int = 0, message: str = "success") -> dict:
                response = super().format_success(data, code, message)
                response["timestamp"] = time.time()
                return response
    """

    # 默认成功码
    SUCCESS_CODE = 200
    # 默认成功消息
    SUCCESS_MESSAGE = "success"

    def format_success(
        self,
        data: Any,
        code: int | None = None,
        message: str | None = None,
    ) -> dict:
        """
        格式化成功响应

        Args:
            data: 响应数据
            code: 成功码，默认为 SUCCESS_CODE
            message: 成功消息，默认为 SUCCESS_MESSAGE

        Returns:
            格式化后的成功响应字典
        """
        return {
            "result": True,
            "code": code if code is not None else self.SUCCESS_CODE,
            "message": message if message is not None else self.SUCCESS_MESSAGE,
            "data": data,
        }

    def format_error(
        self,
        code: int,
        message: str,
        data: Any = None,
        error: dict | None = None,
    ) -> dict:
        """
        格式化错误响应

        Args:
            code: 错误码
            message: 错误消息
            data: 附加数据，默认为 None
            error: 详细错误信息字典，默认为 None

        Returns:
            格式化后的错误响应字典
        """
        return {
            "result": False,
            "code": code,
            "message": message,
            "data": data,
            "error": error,
        }

    def build_error_detail(
        self,
        error_type: str,
        code: int,
        message: str,
        **extra: Any,
    ) -> dict:
        """
        构建错误详情字典

        用于构建 error 字段的标准结构。

        Args:
            error_type: 错误类型名称
            code: 错误码
            message: 错误消息
            **extra: 额外的错误信息字段

        Returns:
            错误详情字典
        """
        error_detail = {
            "type": error_type,
            "code": code,
            "message": message,
        }
        error_detail.update(extra)
        return error_detail
