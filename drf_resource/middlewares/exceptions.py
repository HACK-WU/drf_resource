"""
Trace ID 中间件

提供分布式追踪支持，实现 trace_id 的自动提取、存储和传递。

功能：
1. 从请求头提取 trace_id（X-Trace-ID）
2. 存储到线程本地变量
3. 在响应头中返回 trace_id
4. 自动生成 trace_id（如果请求中不存在）

配置示例：
    MIDDLEWARE = [
        'drf_resource.exceptions.middleware.TraceIdMiddleware',
        ...
    ]
"""

from drf_resource.utils.local import local as _thread_local
from uuid import uuid4


def get_current_trace_id() -> str | None:
    """
    获取当前线程的 trace_id

    Returns:
        当前线程的 trace_id，如果不存在则返回 None
    """
    return getattr(_thread_local, "trace_id", None)


def set_current_trace_id(trace_id: str) -> None:
    """
    设置当前线程的 trace_id

    Args:
        trace_id: 要设置的 trace_id
    """
    _thread_local.trace_id = trace_id


def clear_current_trace_id() -> None:
    """
    清除当前线程的 trace_id

    在请求结束时调用，避免线程复用导致的 trace_id 泄漏
    """
    if hasattr(_thread_local, "trace_id"):
        delattr(_thread_local, "trace_id")


class TraceIdMiddleware:
    """
    Trace ID 中间件

    功能：
    1. 从请求头提取 trace_id（X-Trace-ID）
    2. 存储到线程本地变量，供异常上下文使用
    3. 在响应头中返回 trace_id
    4. 自动生成新的 trace_id（如果请求中不存在）

    配置：
        MIDDLEWARE = [
            'drf_resource.exceptions.middleware.TraceIdMiddleware',
            ...
        ]

    使用示例：
        # 在代码中获取当前 trace_id
        from drf_resource.common_errors.exceptions .middleware import get_current_trace_id

        trace_id = get_current_trace_id()
        print(f"Current trace_id: {trace_id}")

    跨服务调用示例：
        import requests
        from drf_resource.common_errors.exceptions .middleware import get_current_trace_id

        def call_downstream_service():
            trace_id = get_current_trace_id()
            response = requests.post(
                'https://service-b.com/api/endpoint',
                headers={'X-Trace-ID': trace_id}
            )
            return response
    """

    # 请求头名称，可通过子类覆盖自定义
    TRACE_ID_HEADER = "X-Trace-ID"

    # Django 请求头格式（HTTP_ 前缀 + 大写 + 下划线替换连字符）
    TRACE_ID_META_KEY = "HTTP_X_TRACE_ID"

    def __init__(self, get_response):
        """
        初始化中间件

        Args:
            get_response: Django 的响应处理函数
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        处理请求

        Args:
            request: Django 请求对象

        Returns:
            Django 响应对象
        """
        # 从请求头获取或生成 trace_id
        trace_id = self._get_or_create_trace_id(request)

        # 存储到线程本地变量
        set_current_trace_id(trace_id)

        # 添加到 request 对象，方便在视图中直接访问
        request.trace_id = trace_id

        try:
            # 处理请求
            response = self.get_response(request)

            # 在响应头中返回 trace_id
            response[self.TRACE_ID_HEADER] = trace_id

            return response
        finally:
            # 清理线程本地变量，避免线程复用导致的问题
            clear_current_trace_id()

    def _get_or_create_trace_id(self, request) -> str:
        """
        从请求中获取或创建 trace_id

        优先级：
        1. 请求头中的 X-Trace-ID
        2. 生成新的 UUID4

        Args:
            request: Django 请求对象

        Returns:
            trace_id 字符串
        """
        # 尝试从请求头获取
        trace_id = request.META.get(self.TRACE_ID_META_KEY)

        # 也支持从 headers 属性获取（Django 2.2+）
        if not trace_id and hasattr(request, "headers"):
            trace_id = request.headers.get(self.TRACE_ID_HEADER)

        # 如果没有，生成新的
        if not trace_id:
            trace_id = str(uuid4())

        return trace_id


class AsyncTraceIdMiddleware:
    """
    异步 Trace ID 中间件

    用于 Django 异步视图的 trace_id 处理。

    注意：
    - 异步环境下线程本地变量可能不可靠
    - 建议结合 contextvars 使用（Python 3.7+）

    配置：
        MIDDLEWARE = [
            'drf_resource.exceptions.middleware.AsyncTraceIdMiddleware',
            ...
        ]
    """

    TRACE_ID_HEADER = "X-Trace-ID"
    TRACE_ID_META_KEY = "HTTP_X_TRACE_ID"

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        """异步处理请求"""
        # 从请求头获取或生成 trace_id
        trace_id = self._get_or_create_trace_id(request)

        # 存储到线程本地变量（异步环境下可能需要 contextvars）
        set_current_trace_id(trace_id)

        # 添加到 request 对象
        request.trace_id = trace_id

        try:
            # 处理请求
            response = await self.get_response(request)

            # 在响应头中返回 trace_id
            response[self.TRACE_ID_HEADER] = trace_id

            return response
        finally:
            clear_current_trace_id()

    def _get_or_create_trace_id(self, request) -> str:
        """从请求中获取或创建 trace_id"""
        trace_id = request.META.get(self.TRACE_ID_META_KEY)

        if not trace_id and hasattr(request, "headers"):
            trace_id = request.headers.get(self.TRACE_ID_HEADER)

        if not trace_id:
            trace_id = str(uuid4())

        return trace_id
