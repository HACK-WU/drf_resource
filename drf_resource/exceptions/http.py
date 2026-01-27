"""
HTTP 相关异常类

提供与 HTTP 状态码对应的异常类型，用于处理 RESTful API 中的常见错误场景。

Classes:
    HTTPException: HTTP 异常基类
    NotFoundError: 资源不存在 (404)
    PermissionDeniedError: 权限不足 (403)
    UnauthorizedError: 未认证 (401)
    MethodNotAllowedError: 方法不允许 (405)
"""

import logging

from .base import ResourceException
from .codes import StandardErrorCodes


class HTTPException(ResourceException):
    """
    HTTP 相关异常基类

    所有 HTTP 层面的异常都应继承此类。

    Example:
        class ConflictError(HTTPException):
            default_error_code = ErrorCode(3004, "error.conflict", "Resource conflict", 409)
    """

    pass


class NotFoundError(HTTPException):
    """
    资源不存在异常

    当请求的资源不存在时抛出此异常。

    Attributes:
        default_error_code: NOT_FOUND (3000)
        http_status: 404
        log_level: WARNING

    Example:
        # 基础用法
        raise NotFoundError()

        # 指定资源类型
        raise NotFoundError(resource_type="User")

        # 指定资源类型和 ID
        raise NotFoundError(resource_type="User", resource_id="12345")
    """

    default_error_code = StandardErrorCodes.NOT_FOUND
    log_level = logging.WARNING

    def __init__(
        self, resource_type: str = "Resource", resource_id: str | None = None, **kwargs
    ):
        """
        初始化 NotFoundError

        Args:
            resource_type: 资源类型名称，如 "User", "Order" 等
            resource_id: 资源标识符
            **kwargs: 传递给父类的其他参数
        """
        self._resource_type = resource_type
        self._resource_id = resource_id

        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message=message, **kwargs)

    @property
    def resource_type(self) -> str:
        """资源类型"""
        return self._resource_type

    @property
    def resource_id(self) -> str | None:
        """资源 ID"""
        return self._resource_id


class PermissionDeniedError(HTTPException):
    """
    权限不足异常

    当用户没有足够权限执行操作时抛出此异常。

    Attributes:
        default_error_code: PERMISSION_DENIED (3001)
        http_status: 403
        log_level: WARNING

    Example:
        raise PermissionDeniedError()
        raise PermissionDeniedError(message="You don't have permission to delete this resource")
        raise PermissionDeniedError(action="delete", resource="User")
    """

    default_error_code = StandardErrorCodes.PERMISSION_DENIED
    log_level = logging.WARNING

    def __init__(
        self, action: str | None = None, resource: str | None = None, **kwargs
    ):
        """
        初始化 PermissionDeniedError

        Args:
            action: 被拒绝的操作，如 "delete", "update" 等
            resource: 相关资源类型
            **kwargs: 传递给父类的其他参数
        """
        self._action = action
        self._resource = resource

        # 如果没有提供自定义消息，则根据 action 和 resource 生成
        if "message" not in kwargs:
            if action and resource:
                kwargs["message"] = f"Permission denied to {action} {resource}"
            elif action:
                kwargs["message"] = f"Permission denied to {action}"

        super().__init__(**kwargs)

    @property
    def action(self) -> str | None:
        """被拒绝的操作"""
        return self._action

    @property
    def resource(self) -> str | None:
        """相关资源"""
        return self._resource


class UnauthorizedError(HTTPException):
    """
    未认证异常

    当用户未进行身份认证或认证信息无效时抛出此异常。

    Attributes:
        default_error_code: UNAUTHORIZED (3002)
        http_status: 401
        log_level: WARNING

    Example:
        raise UnauthorizedError()
        raise UnauthorizedError(message="Token has expired")
        raise UnauthorizedError(auth_type="Bearer")
    """

    default_error_code = StandardErrorCodes.UNAUTHORIZED
    log_level = logging.WARNING

    def __init__(self, auth_type: str | None = None, **kwargs):
        """
        初始化 UnauthorizedError

        Args:
            auth_type: 认证类型，如 "Bearer", "Basic" 等
            **kwargs: 传递给父类的其他参数
        """
        self._auth_type = auth_type

        if "message" not in kwargs and auth_type:
            kwargs["message"] = f"{auth_type} authentication required"

        super().__init__(**kwargs)

    @property
    def auth_type(self) -> str | None:
        """认证类型"""
        return self._auth_type


class MethodNotAllowedError(HTTPException):
    """
    方法不允许异常

    当请求使用了不支持的 HTTP 方法时抛出此异常。

    Attributes:
        default_error_code: METHOD_NOT_ALLOWED (3003)
        http_status: 405
        log_level: WARNING

    Example:
        raise MethodNotAllowedError()
        raise MethodNotAllowedError(method="DELETE")
        raise MethodNotAllowedError(method="DELETE", allowed_methods=["GET", "POST"])
    """

    default_error_code = StandardErrorCodes.METHOD_NOT_ALLOWED
    log_level = logging.WARNING

    def __init__(
        self, method: str | None = None, allowed_methods: list | None = None, **kwargs
    ):
        """
        初始化 MethodNotAllowedError

        Args:
            method: 被拒绝的 HTTP 方法
            allowed_methods: 允许的 HTTP 方法列表
            **kwargs: 传递给父类的其他参数
        """
        self._method = method
        self._allowed_methods = allowed_methods or []

        if "message" not in kwargs:
            if method and allowed_methods:
                allowed = ", ".join(allowed_methods)
                kwargs["message"] = (
                    f"Method '{method}' not allowed. Allowed methods: {allowed}"
                )
            elif method:
                kwargs["message"] = f"Method '{method}' not allowed"

        super().__init__(**kwargs)

    @property
    def method(self) -> str | None:
        """被拒绝的方法"""
        return self._method

    @property
    def allowed_methods(self) -> list:
        """允许的方法列表"""
        return self._allowed_methods


class ConflictError(HTTPException):
    """
    资源冲突异常

    当请求与服务器当前状态冲突时抛出此异常（如并发更新冲突）。

    Attributes:
        default_error_code: CONFLICT (3004)
        http_status: 409
        log_level: WARNING

    Example:
        raise ConflictError()
        raise ConflictError(message="Resource version conflict")
        raise ConflictError(resource_type="Order", conflict_reason="Already processed")
    """

    default_error_code = StandardErrorCodes.CONFLICT
    log_level = logging.WARNING

    def __init__(
        self,
        resource_type: str | None = None,
        conflict_reason: str | None = None,
        **kwargs,
    ):
        """
        初始化 ConflictError

        Args:
            resource_type: 发生冲突的资源类型
            conflict_reason: 冲突原因
            **kwargs: 传递给父类的其他参数
        """
        self._resource_type = resource_type
        self._conflict_reason = conflict_reason

        if "message" not in kwargs:
            parts = []
            if resource_type:
                parts.append(f"{resource_type} conflict")
            else:
                parts.append("Resource conflict")
            if conflict_reason:
                parts.append(conflict_reason)
            kwargs["message"] = ": ".join(parts)

        super().__init__(**kwargs)

    @property
    def resource_type(self) -> str | None:
        """资源类型"""
        return self._resource_type

    @property
    def conflict_reason(self) -> str | None:
        """冲突原因"""
        return self._conflict_reason


class RateLimitExceededError(HTTPException):
    """
    请求频率超限异常

    当客户端请求频率超过限制时抛出此异常。

    Attributes:
        default_error_code: RATE_LIMIT_EXCEEDED (3005)
        http_status: 429
        log_level: WARNING

    Example:
        raise RateLimitExceededError()
        raise RateLimitExceededError(retry_after=60)
    """

    default_error_code = StandardErrorCodes.RATE_LIMIT_EXCEEDED
    log_level = logging.WARNING

    def __init__(self, retry_after: int | None = None, **kwargs):
        """
        初始化 RateLimitExceededError

        Args:
            retry_after: 建议客户端重试的等待时间（秒）
            **kwargs: 传递给父类的其他参数
        """
        self._retry_after = retry_after

        if "message" not in kwargs:
            if retry_after:
                kwargs["message"] = (
                    f"Rate limit exceeded. Retry after {retry_after} seconds"
                )
            else:
                kwargs["message"] = "Rate limit exceeded"

        super().__init__(**kwargs)

    @property
    def retry_after(self) -> int | None:
        """重试等待时间（秒）"""
        return self._retry_after
