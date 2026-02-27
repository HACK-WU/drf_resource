"""
OpenTelemetry 集成模块

提供与 OpenTelemetry 分布式追踪系统的集成支持。

使用前需要安装 opentelemetry-api:
    pip install opentelemetry-api

Example:
    from drf_resource.utils.opentelemetry import (
        get_trace_id_from_otel,
        get_span_id_from_otel,
    )

    trace_id = get_trace_id_from_otel()
    span_id = get_span_id_from_otel()
"""

# 检测 OpenTelemetry 是否可用
try:
    from opentelemetry import trace
    from opentelemetry.trace import get_current_span, INVALID_SPAN

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    get_current_span = None
    INVALID_SPAN = None


def is_opentelemetry_available() -> bool:
    """
    检查 OpenTelemetry 是否可用

    Returns:
        bool: True 如果 opentelemetry-api 已安装且可用
    """
    return OPENTELEMETRY_AVAILABLE


def _get_span_context():
    """
    获取当前有效的 span context

    Returns:
        Optional[SpanContext]: 有效的 span context，如果不可用则返回 None
    """
    if not OPENTELEMETRY_AVAILABLE:
        return None

    try:
        span = get_current_span()
        # 检查是否是有效的 span
        if span is None or span == INVALID_SPAN:
            return None

        span_context = span.get_span_context()
        if span_context is None or not span_context.is_valid:
            return None

        return span_context
    except Exception:
        # 任何异常都返回 None，不影响主流程
        return None


def get_trace_id_from_otel() -> str | None:
    """
    从 OpenTelemetry 当前 span 获取 trace_id

    返回 32 位十六进制字符串（OpenTelemetry 标准格式）

    Returns:
        Optional[str]: trace_id 字符串，如果不可用则返回 None

    Example:
        >>> trace_id = get_trace_id_from_otel()
        >>> print(trace_id)
        '0af7651916cd43dd8448eb211c80319c'
    """
    span_context = _get_span_context()
    if span_context is None:
        return None

    # trace_id 是 128 位整数，格式化为 32 位十六进制
    return format(span_context.trace_id, "032x")


def get_span_id_from_otel() -> str | None:
    """
    从 OpenTelemetry 当前 span 获取 span_id

    返回 16 位十六进制字符串

    Returns:
        Optional[str]: span_id 字符串，如果不可用则返回 None

    Example:
        >>> span_id = get_span_id_from_otel()
        >>> print(span_id)
        '00f067aa0ba902b7'
    """
    span_context = _get_span_context()
    if span_context is None:
        return None

    # span_id 是 64 位整数，格式化为 16 位十六进制
    return format(span_context.span_id, "016x")


def get_trace_context_from_otel() -> dict | None:
    """
    获取完整的 OpenTelemetry 追踪上下文

    Returns:
        Optional[dict]: 包含 trace_id 和 span_id 的字典，如果不可用则返回 None

    Example:
        >>> context = get_trace_context_from_otel()
        >>> print(context)
        {'trace_id': '0af7651916cd43dd8448eb211c80319c', 'span_id': '00f067aa0ba902b7'}
    """
    trace_id = get_trace_id_from_otel()
    span_id = get_span_id_from_otel()

    if trace_id is None and span_id is None:
        return None

    return {
        "trace_id": trace_id,
        "span_id": span_id,
    }


__all__ = [
    "OPENTELEMETRY_AVAILABLE",
    "is_opentelemetry_available",
    "get_trace_id_from_otel",
    "get_span_id_from_otel",
    "get_trace_context_from_otel",
]
