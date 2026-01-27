"""
DRF-Resource 错误码系统

提供可扩展的错误码定义和注册机制。

Example:
    from drf_resource.exceptions.codes import (
        ErrorCode,
        ErrorCodeRegistry,
        StandardErrorCodes,
    )

    # 使用标准错误码
    code = StandardErrorCodes.NOT_FOUND

    # 注册自定义错误码
    MY_ERROR = ErrorCodeRegistry.register(
        ErrorCode(5001, "error.custom", "Custom error", 400)
    )
"""

from dataclasses import dataclass
from enum import IntEnum


class ErrorCodeRange(IntEnum):
    """
    错误码范围枚举

    定义不同类别错误码的起始值，支持业务扩展。

    范围划分:
        - 1000-1999: 系统级别错误
        - 2000-2999: 参数验证错误
        - 3000-3999: HTTP 错误
        - 4000-4999: 外部 API 错误
        - 5000+: 业务逻辑错误（用户自定义）
    """

    # 系统级别 (1000-1999)
    SYSTEM = 1000
    # 参数验证 (2000-2999)
    VALIDATION = 2000
    # HTTP 错误 (3000-3999)
    HTTP = 3000
    # 外部 API (4000-4999)
    EXTERNAL_API = 4000
    # 业务逻辑 (5000+)
    BUSINESS = 5000


@dataclass(frozen=True)
class ErrorCode:
    """
    错误码定义

    Attributes:
        code: 错误码数值
        message_key: 用于 i18n 的消息键
        default_message: 默认错误消息（当 i18n 未配置时使用）
        http_status: 对应的 HTTP 状态码，默认 500

    Example:
        NOT_FOUND = ErrorCode(3000, "error.not_found", "Resource not found", 404)
    """

    code: int
    message_key: str
    default_message: str
    http_status: int = 500

    def __str__(self) -> str:
        return f"{self.code}"

    def __repr__(self) -> str:
        return f"ErrorCode({self.code}, {self.message_key!r}, {self.default_message!r}, {self.http_status})"


class ErrorCodeRegistry:
    """
    错误码注册表

    支持运行时注册自定义错误码，确保错误码唯一性。

    Example:
        # 注册自定义错误码
        ORDER_NOT_FOUND = ErrorCodeRegistry.register(
            ErrorCode(5001, "error.order_not_found", "Order not found", 404)
        )

        # 获取已注册的错误码
        code = ErrorCodeRegistry.get(5001)

        # 获取所有已注册的错误码
        all_codes = ErrorCodeRegistry.all()
    """

    _codes: dict[int, ErrorCode] = {}

    @classmethod
    def register(cls, error_code: ErrorCode) -> ErrorCode:
        """
        注册错误码

        Args:
            error_code: 要注册的错误码

        Returns:
            注册成功的错误码

        Raises:
            ValueError: 当错误码已存在时
        """
        if error_code.code in cls._codes:
            existing = cls._codes[error_code.code]
            raise ValueError(
                f"Error code {error_code.code} already registered as '{existing.message_key}'"
            )
        cls._codes[error_code.code] = error_code
        return error_code

    @classmethod
    def get(cls, code: int) -> ErrorCode | None:
        """
        获取错误码

        Args:
            code: 错误码数值

        Returns:
            错误码对象，如果不存在则返回 None
        """
        return cls._codes.get(code)

    @classmethod
    def all(cls) -> dict[int, ErrorCode]:
        """
        获取所有已注册的错误码

        Returns:
            错误码字典的副本
        """
        return cls._codes.copy()

    @classmethod
    def clear(cls) -> None:
        """
        清空所有已注册的错误码（仅用于测试）
        """
        cls._codes.clear()

    @classmethod
    def unregister(cls, code: int) -> ErrorCode | None:
        """
        注销错误码

        Args:
            code: 要注销的错误码数值

        Returns:
            被注销的错误码，如果不存在则返回 None
        """
        return cls._codes.pop(code, None)


class StandardErrorCodes:
    """
    标准错误码集合

    提供框架内置的标准错误码，覆盖常见的错误场景。

    错误码范围:
        - 1000-1999: 系统级别错误
        - 2000-2999: 参数验证错误
        - 3000-3999: HTTP 错误
        - 4000-4999: 外部 API 错误

    Example:
        from drf_resource.exceptions.codes import StandardErrorCodes

        # 使用标准错误码
        raise ResourceException(error_code=StandardErrorCodes.NOT_FOUND)
    """

    # ==================== 系统级别 (1000-1999) ====================
    INTERNAL_ERROR = ErrorCode(1000, "error.internal", "Internal server error", 500)
    SERVICE_UNAVAILABLE = ErrorCode(
        1001, "error.unavailable", "Service unavailable", 503
    )
    NOT_IMPLEMENTED = ErrorCode(1002, "error.not_implemented", "Not implemented", 501)
    CONFIGURATION_ERROR = ErrorCode(
        1003, "error.configuration", "Configuration error", 500
    )

    # ==================== 参数验证 (2000-2999) ====================
    VALIDATION_ERROR = ErrorCode(2000, "error.validation", "Validation error", 400)
    PARAMETER_MISSING = ErrorCode(
        2001, "error.param_missing", "Required parameter missing", 400
    )
    PARAMETER_INVALID = ErrorCode(
        2002, "error.param_invalid", "Invalid parameter value", 400
    )
    PARAMETER_TYPE_ERROR = ErrorCode(
        2003, "error.param_type", "Parameter type error", 400
    )
    PARAMETER_FORMAT_ERROR = ErrorCode(
        2004, "error.param_format", "Parameter format error", 400
    )

    # ==================== HTTP 错误 (3000-3999) ====================
    NOT_FOUND = ErrorCode(3000, "error.not_found", "Resource not found", 404)
    PERMISSION_DENIED = ErrorCode(
        3001, "error.permission_denied", "Permission denied", 403
    )
    UNAUTHORIZED = ErrorCode(3002, "error.unauthorized", "Authentication required", 401)
    METHOD_NOT_ALLOWED = ErrorCode(
        3003, "error.method_not_allowed", "Method not allowed", 405
    )
    CONFLICT = ErrorCode(3004, "error.conflict", "Resource conflict", 409)
    RATE_LIMITED = ErrorCode(3005, "error.rate_limited", "Too many requests", 429)
    # 向后兼容别名
    RATE_LIMIT_EXCEEDED = RATE_LIMITED

    # ==================== 外部 API (4000-4999) ====================
    EXTERNAL_API_ERROR = ErrorCode(
        4000, "error.external_api", "External API error", 502
    )
    EXTERNAL_API_TIMEOUT = ErrorCode(
        4001, "error.external_timeout", "External API timeout", 504
    )
    EXTERNAL_API_UNAVAILABLE = ErrorCode(
        4002, "error.external_unavailable", "External service unavailable", 503
    )
    EXTERNAL_API_AUTHENTICATION = ErrorCode(
        4003, "error.external_auth", "External service authentication failed", 502
    )


# 自动注册所有标准错误码
def _register_standard_codes():
    """注册所有标准错误码到注册表"""
    for attr_name in dir(StandardErrorCodes):
        if attr_name.startswith("_"):
            continue
        attr = getattr(StandardErrorCodes, attr_name)
        if isinstance(attr, ErrorCode):
            try:
                ErrorCodeRegistry.register(attr)
            except ValueError:
                # 已注册则跳过
                pass


# 模块加载时自动注册
_register_standard_codes()
