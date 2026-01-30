"""
DRF-Resource Exceptions Module

提供一个全面的 Django REST Framework 异常处理系统。

功能特性:
- 分层架构的异常类体系
- 可扩展的错误码系统
- 自动 trace_id 追踪
- DRF 深度集成
- 国际化支持

Example:
    from drf_resource.common_errors.exceptions  import (
        ResourceException,
        NotFoundError,
        ValidationException,
        ExternalServiceException,
    )

    # 抛出资源不存在错误
    raise NotFoundError(resource_type="User", resource_id="123")

    # 抛出验证错误
    raise ValidationException(message="Invalid input", field="email")

配置 DRF:
    # settings.py
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'drf_resource.exceptions.resource_exception_handler'
    }

    MIDDLEWARE = [
        'drf_resource.exceptions.TraceIdMiddleware',
        ...
    ]
"""

# Base - 基础异常类
from .base import (
    ResourceException,
    ExceptionContext,
    ExceptionDetail,
)

# Error Codes - 错误码系统
from .codes import (
    ErrorCode,
    ErrorCodeRange,
    ErrorCodeRegistry,
    StandardErrorCodes,
)

# HTTP Exceptions - HTTP 异常
from .http import (
    HTTPException,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    MethodNotAllowedError,
    ConflictError,
    RateLimitExceededError,
)

# Validation Exceptions - 验证异常
from .validation import (
    ValidationException,
    ParameterMissingError,
    ParameterInvalidError,
    TypeMismatchError,
    ValueOutOfRangeError,
)

# API Exceptions - 外部服务异常
from .api import (
    ExternalServiceException,
    ServiceTimeoutError,
    ServiceConnectionError,
    ServiceResponseError,
)

# Handlers - DRF 异常处理器
from .handlers import (
    resource_exception_handler,
    ExceptionResponseFormatter,
)

# Middleware - 中间件
from drf_resource.middlewares.exceptions import (
    TraceIdMiddleware,
    get_current_trace_id,
    set_current_trace_id,
)

__all__ = [
    # Base - 基础
    "ResourceException",
    "ExceptionContext",
    "ExceptionDetail",
    # Codes - 错误码
    "ErrorCode",
    "ErrorCodeRange",
    "ErrorCodeRegistry",
    "StandardErrorCodes",
    # HTTP - HTTP 异常
    "HTTPException",
    "NotFoundError",
    "PermissionDeniedError",
    "UnauthorizedError",
    "MethodNotAllowedError",
    "ConflictError",
    "RateLimitExceededError",
    # Validation - 验证异常
    "ValidationException",
    "ParameterMissingError",
    "ParameterInvalidError",
    "TypeMismatchError",
    "ValueOutOfRangeError",
    # API - 外部服务异常
    "ExternalServiceException",
    "ServiceTimeoutError",
    "ServiceConnectionError",
    "ServiceResponseError",
    # Handlers - 处理器
    "resource_exception_handler",
    "ExceptionResponseFormatter",
    # Middleware - 中间件
    "TraceIdMiddleware",
    "get_current_trace_id",
    "set_current_trace_id",
]
