"""
DRF-Resource Exceptions Module

提供一个全面的 Django REST Framework 异常处理系统。

功能特性:
- 分层架构的异常类体系
- 可扩展的错误码系统
- 自动 trace_id 追踪
- DRF 深度集成
- 国际化支持
- OpenTelemetry 集成

Example:
    from drf_resource.exceptions import (
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
from drf_resource.exceptions.base import (
    ResourceException,
    ExceptionContext,
    ExceptionDetail,
)

# Error Codes - 错误码系统
from drf_resource.exceptions.codes import (
    ErrorCode,
    ErrorCodeRange,
    ErrorCodeRegistry,
    StandardErrorCodes,
)

# HTTP Exceptions - HTTP 异常
from drf_resource.exceptions.http import (
    HTTPException,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    MethodNotAllowedError,
    ConflictError,
    RateLimitExceededError,
)

# Validation Exceptions - 验证异常
from drf_resource.exceptions.validation import (
    ValidationException,
    ParameterMissingError,
    ParameterInvalidError,
    TypeMismatchError,
    ValueOutOfRangeError,
)

# API Exceptions - 外部服务异常
from drf_resource.exceptions.api import (
    ExternalServiceException,
    ServiceTimeoutError,
    ServiceConnectionError,
    ServiceResponseError,
)

# Handlers - DRF 异常处理器
from drf_resource.exceptions.handlers import (
    resource_exception_handler,
    ExceptionResponseFormatter,
)

# Middleware - 中间件
from drf_resource.middlewares.exceptions import (
    TraceIdMiddleware,
    get_current_trace_id,
    set_current_trace_id,
)

# OpenTelemetry - 分布式追踪集成（已移至 utils 模块）
from drf_resource.utils.opentelemetry import (
    OPENTELEMETRY_AVAILABLE,
    is_opentelemetry_available,
    get_trace_id_from_otel,
    get_span_id_from_otel,
    get_trace_context_from_otel,
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
    # OpenTelemetry - 分布式追踪
    "OPENTELEMETRY_AVAILABLE",
    "is_opentelemetry_available",
    "get_trace_id_from_otel",
    "get_span_id_from_otel",
    "get_trace_context_from_otel",
]
