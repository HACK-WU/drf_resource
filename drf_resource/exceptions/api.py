"""
API 异常类模块

提供外部服务调用相关的异常类：
- ExternalServiceException: 外部服务调用异常基类
- ServiceTimeoutError: 服务调用超时异常
"""

from .base import ResourceException
from .codes import StandardErrorCodes


class ExternalServiceException(ResourceException):
    """
    外部服务调用异常基类

    用于封装调用外部 API/服务时发生的错误。

    Attributes:
        service_name: 服务名称
        endpoint: 调用的端点
        response_code: 响应状态码

    Example:
        raise ExternalServiceException(
            service_name="PaymentGateway",
            endpoint="/api/v1/charge",
            response_code=500,
            response_message="Service temporarily unavailable"
        )
    """

    default_error_code = StandardErrorCodes.EXTERNAL_API_ERROR

    def __init__(
        self,
        service_name: str,
        endpoint: str | None = None,
        response_code: int | None = None,
        response_message: str | None = None,
        **kwargs,
    ):
        self._service_name = service_name
        self._endpoint = endpoint
        self._response_code = response_code

        # 构建错误消息
        message_parts = [f"Error calling service '{service_name}'"]
        if endpoint:
            message_parts.append(f"endpoint: {endpoint}")
        if response_code is not None:
            message_parts.append(f"response code: {response_code}")
        if response_message:
            message_parts.append(f"message: {response_message}")

        super().__init__(message=", ".join(message_parts), **kwargs)

    @property
    def service_name(self) -> str:
        """服务名称"""
        return self._service_name

    @property
    def endpoint(self) -> str | None:
        """调用端点"""
        return self._endpoint

    @property
    def response_code(self) -> int | None:
        """响应状态码"""
        return self._response_code

    def to_dict(self) -> dict:
        """转换为字典格式，包含服务调用详情"""
        result = super().to_dict()
        result["error"]["service_name"] = self._service_name
        if self._endpoint:
            result["error"]["endpoint"] = self._endpoint
        if self._response_code is not None:
            result["error"]["response_code"] = self._response_code
        return result


class ServiceTimeoutError(ExternalServiceException):
    """
    服务调用超时异常

    当外部服务调用超时时抛出。

    Example:
        raise ServiceTimeoutError(
            service_name="ExternalAPI",
            timeout_seconds=30.0
        )
    """

    default_error_code = StandardErrorCodes.EXTERNAL_API_TIMEOUT

    def __init__(
        self, service_name: str, timeout_seconds: float | None = None, **kwargs
    ):
        self._timeout_seconds = timeout_seconds

        response_message = "Request timed out"
        if timeout_seconds is not None:
            response_message = f"Request timed out after {timeout_seconds}s"

        super().__init__(
            service_name=service_name, response_message=response_message, **kwargs
        )

    @property
    def timeout_seconds(self) -> float | None:
        """超时时间（秒）"""
        return self._timeout_seconds


class ServiceConnectionError(ExternalServiceException):
    """
    服务连接异常

    当无法连接到外部服务时抛出。

    Example:
        raise ServiceConnectionError(
            service_name="DatabaseService",
            reason="Connection refused"
        )
    """

    default_error_code = StandardErrorCodes.EXTERNAL_API_ERROR

    def __init__(self, service_name: str, reason: str | None = None, **kwargs):
        response_message = "Connection failed"
        if reason:
            response_message = f"Connection failed: {reason}"

        super().__init__(
            service_name=service_name, response_message=response_message, **kwargs
        )


class ServiceResponseError(ExternalServiceException):
    """
    服务响应异常

    当外部服务返回非预期响应时抛出。

    Example:
        raise ServiceResponseError(
            service_name="AuthService",
            endpoint="/api/v1/token",
            response_code=401,
            response_message="Invalid credentials"
        )
    """

    def __init__(
        self,
        service_name: str,
        endpoint: str | None = None,
        response_code: int | None = None,
        response_message: str | None = None,
        response_body: dict | None = None,
        **kwargs,
    ):
        self._response_body = response_body

        super().__init__(
            service_name=service_name,
            endpoint=endpoint,
            response_code=response_code,
            response_message=response_message,
            **kwargs,
        )

    @property
    def response_body(self) -> dict | None:
        """响应体内容"""
        return self._response_body

    def to_dict(self) -> dict:
        """转换为字典格式，包含响应体"""
        result = super().to_dict()
        if self._response_body is not None:
            result["error"]["response_body"] = self._response_body
        return result
