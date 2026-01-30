"""
DRF-Resource Exceptions 兼容层

向后兼容层，提供旧 errors 模块的别名映射。
建议在项目迁移完成后移除此模块。

映射关系:
    - Error -> ResourceException
    - ErrorDetails -> ExceptionDetail
    - APIError -> ExternalServiceException
    - CommonError -> ResourceException
    - CustomError -> ResourceException
    - DrfApiError -> ValidationException
    - HTTP404Error -> NotFoundError

Usage:
    # 旧代码（已废弃）
    from drf_resource.common_errors.exceptions .compat import Error, APIError

    # 新代码（推荐）
    from drf_resource.common_errors.exceptions  import ResourceException, ExternalServiceException
"""

import warnings

# 导入新的异常类
from .base import ResourceException, ExceptionDetail, ExceptionContext
from .http import (
    HTTPException,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    MethodNotAllowedError,
)
from .validation import (
    ValidationException,
    ParameterMissingError,
    ParameterInvalidError,
)
from .api import (
    ExternalServiceException,
    ServiceTimeoutError,
)


def _create_deprecated_alias(old_name: str, new_class: type) -> type:
    """
    创建一个带有废弃警告的别名类

    当别名类被实例化时，会发出 DeprecationWarning。

    Args:
        old_name: 旧的类名
        new_class: 新的类

    Returns:
        包装后的别名类
    """

    class DeprecatedAlias(new_class):
        def __init__(self, *args, **kwargs):
            warnings.warn(
                f"'{old_name}' is deprecated and will be removed in a future version. "
                f"Please use '{new_class.__name__}' instead. "
                f"See the migration guide for details.",
                DeprecationWarning,
                stacklevel=2,
            )
            super().__init__(*args, **kwargs)

    # 保留原类名，便于调试
    DeprecatedAlias.__name__ = old_name
    DeprecatedAlias.__qualname__ = old_name

    return DeprecatedAlias


# 兼容别名映射（使用延迟警告）
Error = _create_deprecated_alias("Error", ResourceException)
"""旧名称，请使用 ResourceException 代替"""

ErrorDetails = ExceptionDetail
"""旧名称，请使用 ExceptionDetail 代替"""

APIError = _create_deprecated_alias("APIError", ExternalServiceException)
"""旧名称，请使用 ExternalServiceException 代替"""

CommonError = _create_deprecated_alias("CommonError", ResourceException)
"""旧名称，请使用 ResourceException 代替"""

CustomError = _create_deprecated_alias("CustomError", ResourceException)
"""旧名称，请使用 ResourceException 代替"""

DrfApiError = _create_deprecated_alias("DrfApiError", ValidationException)
"""旧名称，请使用 ValidationException 代替"""

HTTP404Error = _create_deprecated_alias("HTTP404Error", NotFoundError)
"""旧名称，请使用 NotFoundError 代替"""


# 提供一个辅助函数，帮助用户检查代码中的废弃用法
def check_deprecated_usage():
    """
    检查当前代码中是否使用了废弃的异常类名。

    此函数用于辅助迁移，会打印出所有废弃用法的替换建议。

    Usage:
        from drf_resource.common_errors.exceptions .compat import check_deprecated_usage
        check_deprecated_usage()
    """
    deprecation_map = {
        "Error": "ResourceException",
        "ErrorDetails": "ExceptionDetail",
        "APIError": "ExternalServiceException",
        "CommonError": "ResourceException",
        "CustomError": "ResourceException",
        "DrfApiError": "ValidationException",
        "HTTP404Error": "NotFoundError",
    }

    print("=" * 60)
    print("DRF-Resource Exceptions 迁移指南")
    print("=" * 60)
    print("\n请将以下旧类名替换为新类名:\n")

    for old_name, new_name in deprecation_map.items():
        print(f"  {old_name:20} -> {new_name}")

    print("\n导入路径变更:")
    print("  旧: from drf_resource.errors import Error, APIError")
    print(
        "  新: from drf_resource.common_errors.exceptions  import ResourceException, ExternalServiceException"
    )
    print("\n" + "=" * 60)


__all__ = [
    # 兼容别名
    "Error",
    "ErrorDetails",
    "APIError",
    "CommonError",
    "CustomError",
    "DrfApiError",
    "HTTP404Error",
    # 新类（也导出，方便逐步迁移）
    "ResourceException",
    "ExceptionDetail",
    "ExceptionContext",
    "HTTPException",
    "NotFoundError",
    "PermissionDeniedError",
    "UnauthorizedError",
    "MethodNotAllowedError",
    "ValidationException",
    "ParameterMissingError",
    "ParameterInvalidError",
    "ExternalServiceException",
    "ServiceTimeoutError",
    # 辅助函数
    "check_deprecated_usage",
]
