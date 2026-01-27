"""
DRF-Resource 验证异常模块

提供参数验证相关的异常类。

Example:
    from drf_resource.exceptions import (
        ValidationException,
        ParameterMissingError,
        ParameterInvalidError,
    )

    # 通用验证错误
    raise ValidationException(message="Invalid input data", field="email")

    # 缺少必需参数
    raise ParameterMissingError(param_name="username")

    # 参数值无效
    raise ParameterInvalidError(param_name="age", reason="must be a positive integer")
"""

import logging
from typing import Any

from .base import ExceptionDetail, ResourceException
from .codes import StandardErrorCodes


class ValidationException(ResourceException):
    """
    参数验证异常基类

    用于处理所有类型的输入验证错误，包括：
    - 表单验证失败
    - 序列化器验证失败
    - 请求参数验证失败

    Attributes:
        field: 验证失败的字段名
        errors: 详细的错误列表（支持多字段错误）

    Example:
        # 单字段错误
        raise ValidationException(
            message="Email format is invalid",
            field="email"
        )

        # 多字段错误
        raise ValidationException(
            message="Validation failed",
            errors=[
                {"field": "email", "message": "Invalid format"},
                {"field": "age", "message": "Must be positive"},
            ]
        )
    """

    default_error_code = StandardErrorCodes.VALIDATION_ERROR
    log_level = logging.WARNING

    def __init__(
        self,
        message: str | None = None,
        field: str | None = None,
        errors: list[dict[str, Any]] | None = None,
        **kwargs,
    ):
        """
        初始化验证异常

        Args:
            message: 错误消息
            field: 验证失败的字段名（单字段错误时使用）
            errors: 详细错误列表（多字段错误时使用）
            **kwargs: 传递给父类的其他参数
        """
        self._field = field
        self._errors = errors or []
        super().__init__(message=message, **kwargs)

    @property
    def field(self) -> str | None:
        """验证失败的字段名"""
        return self._field

    @property
    def errors(self) -> list[dict[str, Any]]:
        """详细错误列表"""
        return self._errors

    def get_exception_detail(self) -> ExceptionDetail:
        """获取结构化的异常详情"""
        detail = super().get_exception_detail()
        detail.field = self._field
        return detail

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = super().to_dict()
        if self._errors:
            result["error"]["errors"] = self._errors
        return result


class ParameterMissingError(ValidationException):
    """
    缺少必需参数异常

    当请求中缺少必需的参数时抛出。

    Example:
        raise ParameterMissingError(param_name="user_id")
        # Message: "Required parameter 'user_id' is missing"

        raise ParameterMissingError(
            param_name="email",
            detail="Email is required for account verification"
        )
    """

    default_error_code = StandardErrorCodes.PARAMETER_MISSING

    def __init__(self, param_name: str, **kwargs):
        """
        初始化参数缺失异常

        Args:
            param_name: 缺失的参数名
            **kwargs: 传递给父类的其他参数
        """
        super().__init__(
            message=f"Required parameter '{param_name}' is missing",
            field=param_name,
            **kwargs,
        )


class ParameterInvalidError(ValidationException):
    """
    参数值无效异常

    当参数值不符合预期格式或约束时抛出。

    Example:
        raise ParameterInvalidError(param_name="age")
        # Message: "Invalid value for parameter 'age'"

        raise ParameterInvalidError(
            param_name="email",
            reason="must be a valid email address"
        )
        # Message: "Invalid value for parameter 'email': must be a valid email address"

        raise ParameterInvalidError(
            param_name="status",
            reason="must be one of: active, inactive, pending",
            data={"allowed_values": ["active", "inactive", "pending"]}
        )
    """

    default_error_code = StandardErrorCodes.PARAMETER_INVALID

    def __init__(self, param_name: str, reason: str | None = None, **kwargs):
        """
        初始化参数无效异常

        Args:
            param_name: 无效的参数名
            reason: 无效原因说明
            **kwargs: 传递给父类的其他参数
        """
        message = f"Invalid value for parameter '{param_name}'"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message=message, field=param_name, **kwargs)


class TypeMismatchError(ValidationException):
    """
    类型不匹配异常

    当参数类型与预期不符时抛出。

    Example:
        raise TypeMismatchError(
            param_name="count",
            expected_type="integer",
            actual_type="string"
        )
        # Message: "Parameter 'count' type mismatch: expected integer, got string"
    """

    default_error_code = StandardErrorCodes.PARAMETER_INVALID

    def __init__(
        self,
        param_name: str,
        expected_type: str,
        actual_type: str | None = None,
        **kwargs,
    ):
        """
        初始化类型不匹配异常

        Args:
            param_name: 参数名
            expected_type: 期望的类型
            actual_type: 实际的类型
            **kwargs: 传递给父类的其他参数
        """
        message = f"Parameter '{param_name}' type mismatch: expected {expected_type}"
        if actual_type:
            message = f"{message}, got {actual_type}"
        super().__init__(message=message, field=param_name, **kwargs)


class ValueOutOfRangeError(ValidationException):
    """
    值超出范围异常

    当参数值超出允许范围时抛出。

    Example:
        raise ValueOutOfRangeError(
            param_name="page_size",
            min_value=1,
            max_value=100,
            actual_value=500
        )
        # Message: "Parameter 'page_size' value 500 is out of range [1, 100]"
    """

    default_error_code = StandardErrorCodes.PARAMETER_INVALID

    def __init__(
        self,
        param_name: str,
        min_value: Any | None = None,
        max_value: Any | None = None,
        actual_value: Any | None = None,
        **kwargs,
    ):
        """
        初始化值超出范围异常

        Args:
            param_name: 参数名
            min_value: 最小允许值
            max_value: 最大允许值
            actual_value: 实际值
            **kwargs: 传递给父类的其他参数
        """
        range_parts = []
        if min_value is not None:
            range_parts.append(str(min_value))
        else:
            range_parts.append("-∞")

        if max_value is not None:
            range_parts.append(str(max_value))
        else:
            range_parts.append("+∞")

        message = f"Parameter '{param_name}'"
        if actual_value is not None:
            message = f"{message} value {actual_value}"
        message = f"{message} is out of range [{range_parts[0]}, {range_parts[1]}]"

        super().__init__(
            message=message,
            field=param_name,
            data={
                "min_value": min_value,
                "max_value": max_value,
                "actual_value": actual_value,
            },
            **kwargs,
        )
