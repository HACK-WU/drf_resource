"""
通用 HTTP API 客户端

基于 httpflex.DRFClient 和 drf_resource.Resource 的多重继承实现，
提供统一的 HTTP API 请求能力和 drf_resource 架构支持。

使用示例:
    class MyAPIResource(APIResource):
        base_url = "https://api.example.com"
        module_name = "example"
        action = "/users/"
        method = "GET"

        class RequestSerializer(serializers.Serializer):
            user_id = serializers.IntegerField(required=True)

    # 执行请求
    result = MyAPIResource().request({"user_id": 123})
"""

import logging
from typing import Any

from httpflex import DRFClient
from httpflex.parser import JSONResponseParser, RawResponseParser
from httpflex.formatter import BaseResponseFormatter


from drf_resource.base import Resource
from drf_resource.contrib.cache import CacheResource
from drf_resource.errors.api import APIError

logger = logging.getLogger(__name__)


class APIResourceResponseFormatter(BaseResponseFormatter):
    """
    APIResource 专用响应格式化器

    将 DRFClient 的标准响应格式转换为 APIResource 需要的格式，
    并处理业务逻辑错误。
    """

    def format(  # noqa
        self,
        formated_response,
        parsed_data,
        request_id,
        request_data,
        response_or_exception,
        parse_error,
        base_client_instance,
        **kwargs,
    ):
        """
        格式化响应

        1. 如果 HTTP 请求失败，直接返回格式化的错误响应
        2. 如果业务逻辑失败（result=False），抛出 APIError
        3. 如果成功，根据 IS_STANDARD_FORMAT 返回数据
        """
        # HTTP 请求失败
        if not formated_response.get("result", True):
            return formated_response

        # 获取 APIResource 实例的配置
        api_resource = base_client_instance
        is_standard_format = getattr(api_resource, "IS_STANDARD_FORMAT", True)

        # 解析后的数据
        data = parsed_data

        # 如果是字典，检查业务逻辑是否成功
        if isinstance(data, dict):
            # 检查业务逻辑是否失败
            if not data.get("result", True) and data.get("code", 0) != 0:
                # 业务逻辑失败，设置响应为失败
                formated_response["result"] = False
                formated_response["code"] = data.get("code")
                formated_response["message"] = data.get("message", "")
                formated_response["data"] = data
                return formated_response

            # 业务逻辑成功，根据格式返回数据
            if is_standard_format:
                formated_response["data"] = data.get("data")
            else:
                formated_response["data"] = data
        else:
            # 非字典数据，直接返回
            formated_response["data"] = data

        return formated_response


class APIResource(DRFClient, Resource):
    """
    通用 HTTP API 客户端基类（无缓存）

    通过多重继承结合 httpflex.DRFClient 的 HTTP 能力和
    drf_resource.Resource 的架构支持。

    继承关系:
        - DRFClient: 提供 HTTP 请求能力（Session、重试、连接池、钩子等）
        - Resource: 提供 drf_resource 架构支持（序列化、批量请求等）

    子类必须设置（类属性）:
        - base_url: API 基础 URL
        - module_name: 模块名称（用于日志和错误信息）
        - action: 端点路径（对应 DRFClient 的 endpoint）
        - method: HTTP 方法

    可选配置:
        - TIMEOUT: 超时时间（默认 60 秒）
        - IS_STANDARD_FORMAT: 是否标准响应格式（默认 True）
        - IS_STREAM: 是否流式响应（默认 False）
        - enable_retry: 是否启用重试（默认 False）
        - max_retries: 最大重试次数（默认 0）
        - verify: 是否验证 SSL（默认 False）

    使用示例:
        class UserAPI(APIResource):
            base_url = "https://api.example.com"
            module_name = "user_service"
            action = "/api/v1/users/"
            method = "GET"

        # 单个请求
        result = UserAPI().request({"user_id": 123})

        # 批量请求
        results = UserAPI().bulk_request([
            {"user_id": 1},
            {"user_id": 2},
        ])
    """

    # ========== 必须由子类设置的类属性 ==========
    # API 基础 URL
    base_url: str = ""

    # 模块名称，用于日志和错误信息
    module_name: str = ""

    # 端点路径（对应 DRFClient 的 endpoint）
    action: str = ""

    # HTTP 方法
    method: str = "GET"

    # ========== 基础配置 ==========
    # 请求超时时间（秒）
    TIMEOUT = 60

    # 是否使用标准格式数据（{result, code, message, data}）
    IS_STANDARD_FORMAT = True

    # 是否流式响应（SSE）
    IS_STREAM = False

    # ========== httpflex 配置（继承自 DRFClient） ==========
    # 默认超时时间
    default_timeout = 60

    # SSL 证书验证，默认不验证
    verify = False

    # 重试配置
    enable_retry = False
    max_retries = 0

    # 使用自定义响应格式化器
    response_formatter_class = APIResourceResponseFormatter

    def __init__(self, context=None):
        """
        初始化 APIResource

        完整调用 DRFClient 的初始化逻辑，保留其所有功能：
        - Session 创建和配置
        - 重试策略
        - 连接池
        - 钩子机制
        - 响应解析和格式化
        """
        # 设置 DRFClient 需要的属性
        # endpoint 对应 action
        self.endpoint = self.action

        # 设置超时
        self.default_timeout = self.TIMEOUT

        # 设置响应解析器
        response_parser = (
            RawResponseParser() if self.IS_STREAM else JSONResponseParser()
        )

        # 调用 DRFClient 的初始化（会创建 Session、配置重试等）
        DRFClient.__init__(
            self,
            timeout=self.TIMEOUT,
            verify=self.verify,
            response_parser=response_parser,
        )
        self.context = context

    def _validate_request(self, request_data):
        """
        重写DRFClient._validate_request, 使用 Resource.validate_request_data进行请求校验，
        确保两种校验逻辑流程一致。

        """
        validated_request_data = self.validate_request_data(request_data)
        return validated_request_data

    # ========== 统一 request 接口 ==========

    def request(self, request_data=None, **kwargs):
        """
        执行请求的统一入口

        流程:
            1. 合并参数
            2. 使用 Resource 的 validate_request_data 校验请求
            3. 调用 perform_request 执行请求（使用 DRFClient 的 HTTP 能力）
            4. 使用 Resource 的 validate_response_data 校验响应

        参数:
            request_data: 请求数据字典
            **kwargs: 额外参数，会与 request_data 合并

        返回:
            校验后的响应数据
        """
        request_data = request_data or kwargs

        # 使用 Resource 的请求校验
        validated_request_data = self.validate_request_data(request_data)

        # 执行请求
        response_data = self.perform_request(validated_request_data)

        # 使用 Resource 的响应校验
        validated_response_data = self.validate_response_data(response_data)

        return validated_response_data

    def perform_request(self, validated_request_data) -> Any:
        """
        执行 HTTP 请求

        使用 DRFClient 的 _execute_single_request 执行请求，
        充分利用 DRFClient 的能力：
        - 请求前后钩子
        - 重试机制
        - 响应解析和格式化
        - 错误处理

        参数:
            validated_request_data: 校验后的请求数据

        返回:
            处理后的响应数据
        """
        validated_request_data = dict(validated_request_data)
        validated_request_data = self.full_request_data(validated_request_data)

        # 更新请求头
        headers = self.get_headers()
        self.session.headers.update(headers)

        # 处理流式响应
        if self.IS_STREAM:
            return self._perform_stream_request(validated_request_data)

        # 使用 DRFClient 的 _execute_single_request 执行请求
        result = self._execute_single_request(validated_request_data)

        # 处理响应结果
        return self._handle_response(result, validated_request_data)

    def _perform_stream_request(self, validated_request_data: dict) -> Any:
        """
        执行流式请求

        流式请求需要特殊处理，直接返回 StreamingHttpResponse。
        """
        from django.http import StreamingHttpResponse

        request_url = self.get_request_url(validated_request_data)

        # 构建请求参数
        request_kwargs = {
            "method": self.method.upper(),
            "url": request_url,
            "timeout": self.TIMEOUT,
            "verify": self.verify,
            "stream": True,
        }

        if self.method.upper() == "GET":
            request_kwargs["params"] = validated_request_data
        else:
            request_kwargs["json"] = validated_request_data

        response = self.session.request(**request_kwargs)
        response.raise_for_status()

        def event_stream():
            for line in response.iter_lines():
                if line:
                    yield line.decode("utf-8") + "\n\n"

        sr = StreamingHttpResponse(
            event_stream(), content_type="text/event-stream; charset=utf-8"
        )
        sr.headers["Cache-Control"] = "no-cache"
        sr.headers["X-Accel-Buffering"] = "no"
        return sr

    def _execute_single_request(self, request_data: dict) -> dict:
        """
        执行单个请求

        重写 DRFClient 的方法，添加 APIResource 特定的逻辑。
        """
        request_id = self.generate_request_id()

        # 使用 DRFClient 的 _make_request_and_format
        return self._make_request_and_format(request_id, request_data)

    def _handle_response(self, result: dict, validated_request_data: dict) -> Any:
        """
        处理响应结果

        将 DRFClient 的标准响应格式转换为 APIResource 的返回值。

        参数:
            result: DRFClient 返回的标准格式响应 {result, code, message, data}
            validated_request_data: 原始请求数据

        返回:
            处理后的响应数据

        异常:
            APIError: 当请求失败时抛出
        """
        # 检查请求是否成功
        if not result.get("result", True):
            raise APIError(
                system_name=self.module_name,
                url=self.action,
                result={
                    "code": result.get("code"),
                    "message": result.get("message"),
                },
            )

        # 获取数据
        response_data = result.get("data")

        # 渲染响应数据
        return self.render_response_data(validated_request_data, response_data)

    # ========== DRFClient 钩子方法重写 ==========

    def before_request(self, request_id: str, request_data: dict) -> dict:
        """
        请求前钩子

        子类可覆盖以修改请求数据。
        """
        # 调用父类的钩子
        request_data = super().before_request(request_id, request_data)
        return request_data

    def after_request(self, request_id: str, response) -> Any:
        """
        请求后钩子

        子类可覆盖以处理响应。
        """
        return super().after_request(request_id, response)

    def on_request_error(self, request_id: str, error: Exception) -> None:
        """
        请求错误钩子

        子类可覆盖以处理错误（如上报指标）。
        """
        super().on_request_error(request_id, error)

    # ========== 保留的接口（子类可覆盖） ==========

    def get_headers(self) -> dict:
        """
        获取请求头

        子类可覆盖添加认证头或其他自定义头。
        """
        return {}

    def full_request_data(self, validated_request_data: dict) -> dict:
        """
        丰富请求数据

        子类可覆盖添加通用参数（如用户信息、凭证等）。
        """
        return validated_request_data

    def get_request_url(self, validated_request_data: dict) -> str:
        """
        获取请求 URL

        子类可覆盖以支持路径参数等。
        """
        return self.base_url.rstrip("/") + "/" + self.action.lstrip("/")

    def render_response_data(
        self, validated_request_data: dict, response_data: Any
    ) -> Any:
        """
        渲染响应数据

        在返回响应前对数据进行最后处理。
        """
        return response_data

    # ========== 批量请求（沿用 Resource 的实现） ==========
    # bulk_request 直接继承自 Resource，无需重写

    # ========== 辅助属性 ==========

    @property
    def label(self) -> str:
        """API 标签"""
        return ""

    @property
    def action_display(self) -> str:
        """
        API 描述

        格式: module_name-label
        """
        if self.label:
            return f"{self.module_name}-{self.label}"
        return self.module_name


class APICacheResource(APIResource, CacheResource):
    """
    带缓存的 HTTP API 客户端基类

    继承关系:
        - APIResource: 提供 HTTP 请求能力
        - CacheResource: 提供缓存功能

    MRO: APICacheResource -> APIResource -> DRFClient -> CacheResource -> Resource -> object

    缓存配置（继承自 CacheResource）:
        - cache_type: 缓存类型
        - backend_cache_type: 后台缓存类型
        - cache_user_related: 缓存是否与用户关联
        - cache_compress: 是否压缩缓存

    使用示例:
        from drf_resource.cache import CacheTypeItem

        class CachedUserAPI(APICacheResource):
            base_url = "https://api.example.com"
            module_name = "user_service"
            action = "/api/v1/users/"
            method = "GET"

            # 启用缓存，过期时间 60 秒
            cache_type = CacheTypeItem(timeout=60)
    """

    def __init__(self, context=None):
        """
        初始化 APICacheResource

        需要正确处理多重继承的初始化顺序。
        缓存包装需要在 request 方法初始化之后完成。
        """
        # 先检查是否需要缓存包装
        need_cache = self._need_cache_wrap()

        # 初始化 APIResource（内部会初始化 DRFClient 和 Resource）
        APIResource.__init__(self, context=context)

        # 如果需要缓存，包装 request 方法
        if need_cache:
            self._wrap_request()


# 保留别名以兼容旧代码
BKAPIError = APIError
