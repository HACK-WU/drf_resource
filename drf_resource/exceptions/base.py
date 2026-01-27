"""
DRF-Resource 基础异常模块

提供异常上下文、异常详情和基础异常类。
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from django.utils.translation import gettext as _

from .codes import ErrorCode, StandardErrorCodes


@dataclass
class ExceptionContext:
    """
    异常上下文信息

    仅包含最小必要信息，避免暴露敏感数据：
    - timestamp: 异常发生时间
    - trace_id: 分布式追踪 ID

    获取 trace_id 的优先级：
    1. OpenTelemetry 当前 span 的 trace_id
    2. 从请求头 (X-Trace-ID) 读取
    3. 从线程本地变量读取（通过中间件设置）
    4. 自动生成 UUID4（兜底方案）
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)
    trace_id: str = None

    def __post_init__(self):
        """初始化后自动填充 trace_id"""
        if self.trace_id is None:
            self.trace_id = self._get_trace_id()

    def _get_trace_id(self) -> str:
        """获取 trace_id，按优先级尝试多种来源"""
        # 优先级 1: OpenTelemetry
        trace_id = self._get_trace_id_from_otel()
        if trace_id:
            return trace_id

        # 优先级 2: 线程本地变量
        trace_id = self._get_trace_id_from_thread()
        if trace_id:
            return trace_id

        # 优先级 3: 生成新的 UUID
        return str(uuid4())

    def _get_trace_id_from_otel(self) -> str | None:
        """从 OpenTelemetry 获取 trace_id"""
        try:
            from .contrib.opentelemetry import get_trace_id_from_otel

            return get_trace_id_from_otel()
        except (ImportError, AttributeError):
            return None

    def _get_trace_id_from_thread(self) -> str | None:
        """从线程本地变量获取 trace_id"""
        try:
            from .middleware import get_current_trace_id

            return get_current_trace_id()
        except (ImportError, AttributeError):
            return None

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id,
        }


@dataclass
class ExceptionDetail:
    """异常详情信息"""

    type: str
    code: int
    message: str
    detail: str | None = None
    field: str | None = None  # 用于验证错误
    context: ExceptionContext | None = None

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {
            "type": self.type,
            "code": self.code,
            "message": self.message,
        }
        if self.detail:
            result["detail"] = self.detail
        if self.field:
            result["field"] = self.field
        if self.context:
            result["context"] = self.context.to_dict()
        return result


class ResourceException(Exception):
    """
    DRF-Resource 异常基类

    所有框架异常的根类，提供：
    - 结构化的错误码系统
    - 国际化支持
    - 异常链追踪
    - 上下文信息捕获

    Example:
        raise ResourceException(
            message="Custom error message",
            error_code=StandardErrorCodes.INTERNAL_ERROR,
            detail="Additional details here"
        )
    """

    # 默认错误码，子类应覆盖
    default_error_code: ErrorCode = StandardErrorCodes.INTERNAL_ERROR

    # 日志级别
    log_level: int = logging.ERROR

    def __init__(
        self,
        message: str | None = None,
        error_code: ErrorCode | None = None,
        detail: str | None = None,
        data: Any = None,
        cause: Exception | None = None,
        context: ExceptionContext | None = None,
        **format_kwargs: Any,
    ):
        self._error_code = error_code or self.default_error_code

        # 消息处理：支持模板格式化
        if message is None:
            message = _(self._error_code.default_message)
        elif format_kwargs:
            try:
                message = message.format(**format_kwargs)
            except (KeyError, IndexError):
                pass  # 格式化失败时保留原始消息

        self._message = message
        self._detail = detail
        self._data = data
        self._cause = cause
        self._context = context or ExceptionContext()

        # 设置异常链
        super().__init__(message)
        if cause:
            self.__cause__ = cause

    @property
    def code(self) -> int:
        """错误码"""
        return self._error_code.code

    @property
    def http_status(self) -> int:
        """HTTP 状态码"""
        return self._error_code.http_status

    @property
    def message(self) -> str:
        """错误消息"""
        return self._message

    @property
    def detail(self) -> str | None:
        """错误详情"""
        return self._detail

    @property
    def data(self) -> Any:
        """附加数据"""
        return self._data

    @property
    def context(self) -> ExceptionContext:
        """异常上下文"""
        return self._context

    def get_exception_detail(self) -> ExceptionDetail:
        """获取结构化的异常详情"""
        return ExceptionDetail(
            type=self.__class__.__name__,
            code=self.code,
            message=self.message,
            detail=self.detail,
            context=self._context,
        )

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "result": False,
            "code": self.code,
            "message": self.message,
            "data": self._data,
            "error": self.get_exception_detail().to_dict(),
        }

    def log(self, logger: logging.Logger | None = None):
        """记录日志，自动包含 trace_id"""
        if logger is None:
            logger = logging.getLogger(__name__)

        log_method = getattr(
            logger, logging.getLevelName(self.log_level).lower(), logger.error
        )
        log_method(
            f"[trace_id={self._context.trace_id}] [{self.code}] {self.message}",
            exc_info=self._cause,
        )

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message!r})"
