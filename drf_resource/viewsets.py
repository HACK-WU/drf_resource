"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_control
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from drf_resource.base import Resource
from drf_resource.utils.local import local

"""
Resource的ViewSet定义
"""


class ResourceRoute:
    """
    Resource的视图配置，应用于viewsets
    """

    def __init__(
        self,
        method,
        resource_class,
        endpoint="",
        pk_field=None,
        enable_paginate=False,
        content_encoding=None,
        decorators=None,
    ):
        """
        :param method: 请求方法，目前仅支持GET和POST
        :param resource_class: 所用到的Resource类
        :param endpoint: 端点名称，不提供则为list或create
        :param pk_field: 主键名称，如果不为空，则该视图为 detail route
        :param enable_paginate: 是否对结果进行分页
        :param content_encoding: 返回数据内容编码类型
        :params decorators: 给view_func添加的装饰器列表
        """
        # if method.upper() not in ["GET", "POST"]:
        #     raise ValueError(_("method参数错误，目前仅支持GET或POST方法"))

        self.method = method.upper()

        if isinstance(resource_class, Resource):
            resource_class = resource_class.__class__
        if not issubclass(resource_class, Resource):
            raise ValueError(
                _(
                    "resource_class参数必须提供Resource的子类, 当前类型: {}".format(
                        resource_class
                    )
                )
            )

        self.resource_class = resource_class

        self.endpoint = endpoint

        self.enable_paginate = enable_paginate

        self.content_encoding = content_encoding

        self.pk_field = pk_field

        self.decorators = decorators


class ResourceViewSet(viewsets.GenericViewSet):
    EMPTY_ENDPOINT_METHODS = {
        "GET": "list",
        "POST": "create",
        "PUT": "update",
        "PATCH": "partial_update",
        "DELETE": "destroy",
    }

    # 用于执行请求的Resource类
    resource_routes: list[ResourceRoute] = []
    filter_backends = []
    pagination_class = None
    resource_mapping = {}

    def get_serializer_class(self):
        """
        获取序列化器
        """
        serializer_class = None
        for route in self.resource_routes:
            if self.action == route.endpoint:
                serializer_class = route.resource_class.RequestSerializer
                break

        if not serializer_class:
            serializer_class = Serializer

        class Meta:
            ref_name = None

        # 如果serializer_class没有Meta属性，则添加Meta属性
        if not getattr(serializer_class, "Meta", None):
            serializer_class.Meta = Meta

        return serializer_class

    def get_queryset(self):
        """
        添加默认函数，避免swagger生成报错
        """
        return

    @classmethod
    def generate_endpoint(cls):
        """
        动态生成 ViewSet 的端点方法

        该方法遍历 resource_routes 配置，为每个 ResourceRoute 动态生成对应的视图函数，
        并将其绑定到 ViewSet 类上。支持标准 RESTful 方法和自定义 action 端点。

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                           整体流程图                                         │
        ├─────────────────────────────────────────────────────────────────────────────┤
        │                                                                             │
        │   [开始] ──► 获取 ViewSet 路径                                               │
        │                    │                                                        │
        │                    ▼                                                        │
        │   ┌────────────────────────────────┐                                        │
        │   │  遍历 resource_routes 配置列表  │ ◄─────────────────────┐               │
        │   └────────────────────────────────┘                       │               │
        │                    │                                       │               │
        │                    ▼                                       │               │
        │   ┌────────────────────────────────┐                       │               │
        │   │ 步骤1: 生成基础视图函数         │                       │               │
        │   └────────────────────────────────┘                       │               │
        │                    │                                       │               │
        │                    ▼                                       │               │
        │   ┌────────────────────────────────┐                       │               │
        │   │ 步骤2: 配置 Swagger 文档装饰器  │                       │               │
        │   └────────────────────────────────┘                       │               │
        │                    │                                       │               │
        │                    ▼                                       │               │
        │   ┌────────────────────────────────┐                       │               │
        │   │ 步骤3: 应用自定义装饰器(可选)   │                       │               │
        │   └────────────────────────────────┘                       │               │
        │                    │                                       │               │
        │                    ▼                                       │               │
        │            ┌──────────────┐                                │               │
        │            │ endpoint为空? │                               │               │
        │            └──────────────┘                                │               │
        │              /         \                                   │               │
        │            是           否                                  │               │
        │            /             \                                 │               │
        │           ▼               ▼                                │               │
        │   ┌──────────────┐  ┌──────────────┐                       │               │
        │   │ 绑定标准方法  │  │ 创建自定义    │                       │               │
        │   │ list/create  │  │ action端点   │                       │               │
        │   │ retrieve/... │  │              │                       │               │
        │   └──────────────┘  └──────────────┘                       │               │
        │           \             /                                  │               │
        │            \           /                                   │               │
        │             ▼         ▼                                    │               │
        │        ┌─────────────────────┐                             │               │
        │        │ 注册到resource_mapping│                            │               │
        │        └─────────────────────┘                             │               │
        │                    │                                       │               │
        │                    └───────────────────────────────────────┘               │
        │                    (继续处理下一个route)                                     │
        │                                                                             │
        │              [所有route处理完毕] ──► [结束]                                  │
        │                                                                             │
        └─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                    标准方法映射关系 (endpoint为空时)                          │
        ├─────────────────────────────────────────────────────────────────────────────┤
        │                                                                             │
        │   HTTP方法    pk_field    映射到的ViewSet方法      URL示例                   │
        │   ─────────────────────────────────────────────────────────────────         │
        │   GET         无          list()                  /api/resources/           │
        │   GET         有          retrieve()              /api/resources/{pk}/      │
        │   POST        无          create()                /api/resources/           │
        │   PUT         有          update()                /api/resources/{pk}/      │
        │   PATCH       有          partial_update()        /api/resources/{pk}/      │
        │   DELETE      有          destroy()               /api/resources/{pk}/      │
        │                                                                             │
        └─────────────────────────────────────────────────────────────────────────────┘
        """
        # ========== 获取 ViewSet 的完整模块路径 ==========
        # 用于构建 resource_mapping 的唯一标识 key
        # 区分：cls 本身是 ResourceViewSet 子类 vs cls 是实例
        if issubclass(cls, ResourceViewSet):
            view_set_path = f"{cls.__module__}.{cls.__name__}"
        else:
            view_set_path = f"{type(cls).__module__}.{type(cls).__name__}"

        # ========== 遍历所有路由配置 ==========
        for resource_route in cls.resource_routes:
            # ────────────────────────────────────────────────────────────────
            # 步骤1: 生成基础视图函数
            # ────────────────────────────────────────────────────────────────
            # 调用 _generate_view_function 创建处理 HTTP 请求的视图函数
            function = cls._generate_view_function(resource_route)

            # ────────────────────────────────────────────────────────────────
            # 步骤2: 配置 Swagger 文档装饰器
            # ────────────────────────────────────────────────────────────────
            # 获取请求序列化器（用于文档展示请求参数结构）
            request_serializer_class = (
                resource_route.resource_class.RequestSerializer or Serializer
            )
            request_serializer = request_serializer_class(
                many=resource_route.resource_class.many_request_data
            )

            # 获取响应序列化器（用于文档展示响应数据结构）
            response_serializer_class = (
                resource_route.resource_class.ResponseSerializer or Serializer
            )
            response_serializer = response_serializer_class(
                many=resource_route.resource_class.many_response_data
            )

            # 创建 swagger 装饰器，自动生成 API 文档
            decorator_function = swagger_auto_schema(
                responses={200: response_serializer},  # 200 响应的数据结构
                operation_description=resource_route.resource_class.__doc__,  # 接口描述取自 Resource 类文档
                query_serializer=request_serializer
                if resource_route.method == "GET"
                else None,  # GET 请求展示查询参数
            )

            # ────────────────────────────────────────────────────────────────
            # 步骤3: 应用自定义装饰器（可选）
            # ────────────────────────────────────────────────────────────────
            # 如果配置了额外装饰器，按顺序依次包裹视图函数
            if resource_route.decorators:
                for decorator in resource_route.decorators:
                    function = decorator(function)

            # ────────────────────────────────────────────────────────────────
            # 步骤4: 将视图函数绑定到 ViewSet
            # ────────────────────────────────────────────────────────────────
            #
            # 分支A: endpoint 为空 → 绑定为标准 RESTful 方法
            # 分支B: endpoint 非空 → 创建自定义 action 端点
            #
            if not resource_route.endpoint:
                # ═══════════════════════════════════════════════════════════
                # 分支A: 绑定标准 RESTful 方法 (list/create/retrieve/update/destroy)
                # ═══════════════════════════════════════════════════════════
                function = decorator_function(function)

                # 根据 HTTP 方法 + pk_field 组合，映射到对应的标准方法
                if resource_route.method == "GET":
                    if resource_route.pk_field:
                        # GET + pk_field → retrieve (获取单个资源详情)
                        cls.retrieve = function
                    else:
                        # GET 无 pk_field → list (获取资源列表)
                        cls.list = function

                elif resource_route.method == "POST":
                    # POST 创建资源，不允许设置 pk_field
                    if resource_route.pk_field:
                        raise AssertionError(
                            _(
                                "当请求方法为 %s，且 endpoint 为空时，禁止设置 pk_field 参数"
                            )
                            % resource_route.method
                        )
                    cls.create = function

                elif resource_route.method in cls.EMPTY_ENDPOINT_METHODS:
                    # PUT/PATCH/DELETE 必须指定 pk_field（需要知道操作哪个资源）
                    if not resource_route.pk_field:
                        raise AssertionError(
                            _(
                                "当请求方法为 %s，且 endpoint 为空时，必须提供 pk_field 参数"
                            )
                            % resource_route.method
                        )
                    # 从映射表获取方法名: PUT→update, PATCH→partial_update, DELETE→destroy
                    setattr(
                        cls, cls.EMPTY_ENDPOINT_METHODS[resource_route.method], function
                    )

                else:
                    # 不支持的 HTTP 方法
                    raise AssertionError(
                        _("不支持的请求方法: %s，请确认resource_routes配置是否正确!")
                        % resource_route.method
                    )

                # 注册到映射表: key=(HTTP方法, "模块路径-方法名"), value=Resource类
                cls.resource_mapping[
                    (
                        resource_route.method,
                        f"{view_set_path}-{cls.EMPTY_ENDPOINT_METHODS[resource_route.method]}",
                    )
                ] = resource_route.resource_class

            else:
                # ═══════════════════════════════════════════════════════════
                # 分支B: 创建自定义 action 端点
                # ═══════════════════════════════════════════════════════════

                # 设置函数名（特殊处理 "detail" 避免与 DRF 内置名称冲突）
                function.__name__ = (
                    f"api_func_{resource_route.endpoint}"
                    if resource_route.endpoint == "detail"
                    else resource_route.endpoint
                )

                # 添加缓存控制: 禁用缓存 + 标记为私有响应
                function = method_decorator(cache_control(max_age=0, private=True))(
                    function
                )

                # 使用 DRF @action 装饰器注册为自定义端点
                function = action(
                    detail=bool(
                        resource_route.pk_field
                    ),  # 是否为详情路由 (URL 是否含主键)
                    methods=[resource_route.method],  # 允许的 HTTP 方法
                    url_path=resource_route.endpoint,  # URL 路径后缀
                    url_name=resource_route.endpoint.replace(
                        "_", "-"
                    ),  # URL 名称 (下划线转中划线)
                )(function)

                # 应用 swagger 文档装饰器
                function = decorator_function(function)

                # 将函数绑定到 ViewSet 类
                setattr(cls, function.__name__, function)

                # 注册到映射表: key=(HTTP方法, "模块路径-endpoint名称"), value=Resource类
                cls.resource_mapping[
                    (
                        resource_route.method,
                        f"{view_set_path}-{resource_route.endpoint}",
                    )
                ] = resource_route.resource_class

    @classmethod
    def _generate_view_function(cls, resource_route: ResourceRoute):
        """
        生成方法模版
        """

        def view(self, request, *args, **kwargs):
            resource = resource_route.resource_class()
            params = (
                request.query_params.copy()
                if resource_route.method == "GET"
                else request.data
            )
            local.current_request = request

            if resource_route.pk_field:
                # 如果是detail route，需要重url参数中获取主键，并塞到请求参数中
                params.update({resource_route.pk_field: kwargs[cls.lookup_field]})

            is_async_task = "HTTP_X_ASYNC_TASK" in request.META
            if is_async_task:
                # 执行异步任务
                data = resource.delay(params)
                response = Response(data)
            else:
                data = resource.request(params)
                if isinstance(data, HttpResponse):
                    return data
                if resource_route.enable_paginate:
                    page = self.paginate_queryset(data)
                    response = self.get_paginated_response(page)
                else:
                    response = Response(data)
            if resource_route.content_encoding:
                response.content_encoding = resource_route.content_encoding
            return response

        view.__name__ = resource_route.endpoint
        return view
