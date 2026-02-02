"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc
import logging

from django.db import models
from django.http.response import HttpResponseBase
from django.utils.translation import gettext as _
from drf_resource.exceptions import ResourceException
from drf_resource.tasks import run_perform_request
from drf_resource.tools import (
    format_serializer_errors,
    get_serializer_fields,
    render_schema_structured,
)
from drf_resource.utils.thread_backend import ThreadPool
from drf_resource.utils.user import get_request_username

# OpenTelemetry 可选依赖支持
try:
    from opentelemetry import trace
    from opentelemetry.trace.status import Status, StatusCode

    tracer = trace.get_tracer(__name__)
except ImportError:
    # No-op 降级实现
    class _NoOpTracer:
        def start_as_current_span(self, *args, **kwargs):
            return self._NoOpSpan()

        class _NoOpSpan:
            def __enter__(self):
                return self

            def __exit__(self, *args, **kwargs):
                pass

            def set_status(self, *args, **kwargs):
                pass

            def add_event(self, *args, **kwargs):
                pass

            def record_exception(self, *args, **kwargs):
                pass

    tracer = _NoOpTracer()
    import warnings

    warnings.warn(
        "OpenTelemetry not available, using no-op tracer. "
        "Install opentelemetry to enable tracing."
    )

logger = logging.getLogger(__name__)


__doc__ = """
DRF Resource - 声明式 API 资源框架

这是一个基于 Django REST Framework 的轻量级资源化框架，通过声明式的方式简化 API 开发。

核心概念
--------
Resource 是对业务逻辑的封装单元，负责处理输入数据并返回处理结果。
通过继承 Resource 基类（abc.ABC）实现自定义资源。

基本用法
--------
```python
from rest_framework import serializers
from drf_resource.base import Resource

class MyRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

class MyResource(Resource):
    RequestSerializer = MyRequestSerializer

    def perform_request(self, validated_request_data):
        user_id = validated_request_data['user_id']
        # 业务逻辑处理
        return {'result': 'success', 'user_id': user_id}

# 调用方式
resource = MyResource()
result = resource.request({'user_id': 123})
```

执行流程
--------
1. 实例化 Resource（可传递 context 上下文参数）
2. 自动搜索并绑定 RequestSerializer 和 ResponseSerializer（基于命名约定）
3. 调用 request() 方法，传入请求数据
4. 使用 RequestSerializer 校验输入（如果定义）
5. 调用子类实现的 perform_request() 执行业务逻辑
6. 判断返回值类型：
   - HttpResponse 类型：直接返回（用于渲染页面等场景）
   - 普通数据：使用 ResponseSerializer 校验输出（如果定义）
7. 返回最终结果

命名约定
--------
为了自动发现 Serializer，需遵循以下命名规则：
- Resource 类名：XxxResource
- 请求序列化器：XxxRequestSerializer
- 响应序列化器：XxxResponseSerializer

高级特性
--------
返回 HttpResponse：
    perform_request() 可直接返回 Django 响应对象（HttpResponse、render 结果、
    JsonResponse 等），框架会自动识别并跳过响应数据校验，直接透传给客户端。

    示例：
    ```python
    def perform_request(self, validated_request_data):
        return render(request, 'template.html', context)
    ```

访问请求对象：
    在 ViewSet 中使用时，可通过 self._current_request 访问当前的 Django request 对象。

    示例：
    ```python
    def perform_request(self, validated_request_data):
        user = self._current_request.user
        return {'username': user.username}
    ```

上下文传递：
    初始化时可传递任意上下文参数，通过 self.context 访问。

    示例：
    ```python
    resource = MyResource(context={'db': 'master'})
    # 或
    resource = MyResource(db='master', cache=True)
    ```

异步任务支持：
    支持 Celery 异步任务执行。

    示例：
    ```python
    result = resource.delay({'user_id': 123})  # 返回 task_id
    ```

批量请求：
    支持多线程批量并发请求。

    示例：
    ```python
    results = resource.bulk_request([
        {'user_id': 1},
        {'user_id': 2},
    ])
    ```

注意事项
--------
- perform_request() 是抽象方法，子类必须实现
- RequestSerializer 和 ResponseSerializer 是可选的
- 返回 HttpResponse 时会跳过 ResponseSerializer 校验
- 使用 self._current_request 仅在通过 ViewSet 调用时有效

"""


class Resource(abc.ABC):
    RequestSerializer = None
    ResponseSerializer = None

    # 提供一个serializers模块，在实例化某个Resource时，在该模块内自动查找符合命名
    # 规则的serializers，并进行自动配置
    serializers_module = None

    # 数据是否为对象的列表
    many_request_data = False
    many_response_data = False

    # 支持记录请求参数(settings开启：ENABLE_RESOURCE_DATA_COLLECT后，
    # 记录所有`support_data_collect`为True的resource请求)
    support_data_collect = True

    def __init__(self, *args, **kwargs):
        self.RequestSerializer, self.ResponseSerializer = (
            self._search_serializer_class()
        )
        self.context = kwargs.get("context", kwargs)
        self._task_manager = None
        self._current_request = None

    def __call__(self, *args, **kwargs):
        # thread safe
        tmp_resource = self.__class__()
        from drf_resource.models import ResourceData

        return ResourceData.objects.request(tmp_resource, args, kwargs)

    @property
    def request_serializer(self):
        """
        :rtype: serializers.Serializer
        """
        if not hasattr(self, "_request_serializer"):
            msg = "You must call `.validate_request_data()` before accessing `.request_serializer`."
            raise AssertionError(msg)
        return self._request_serializer

    @property
    def response_serializer(self):
        """
        :rtype: serializers.Serializer
        """
        if not hasattr(self, "_response_serializer"):
            msg = "You must call `.validate_response_data()` before accessing `.response_serializer`."
            raise AssertionError(msg)
        return self._response_serializer

    @classmethod
    def get_resource_name(cls):
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def _search_serializer_class(cls):
        """
        搜索该Resource对应的两个Serializer
        """

        # 若类的内部声明了RequestSerializer和ResponseSerializer，则优先使用
        request_serializer_class = cls.RequestSerializer
        response_serializer_class = cls.ResponseSerializer

        # 若类中没有声明，则对指定模块进行搜索
        resource_name = cls.get_resource_name()
        request_serializer_class_name = f"{resource_name}RequestSerializer"
        response_serializer_class_name = f"{resource_name}ResponseSerializer"

        if cls.serializers_module:
            if not request_serializer_class:
                request_serializer_class = getattr(
                    cls.serializers_module, request_serializer_class_name, None
                )

            if not response_serializer_class:
                response_serializer_class = getattr(
                    cls.serializers_module, response_serializer_class_name, None
                )

        return request_serializer_class, response_serializer_class

    @abc.abstractmethod
    def perform_request(self, validated_request_data):
        """
        此处为Resource的业务逻辑，由子类实现
        将request_data通过一定的逻辑转化为response_data

        example:
            return validated_request_data
        """
        raise NotImplementedError

    def validate_request_data(self, request_data):
        """
        校验请求数据
        """
        self._request_serializer = None
        if not self.RequestSerializer:
            return request_data

        # model类型的数据需要特殊处理
        if isinstance(request_data, models.Model | models.QuerySet):
            request_serializer = self.RequestSerializer(
                request_data, many=self.many_request_data
            )
            self._request_serializer = request_serializer
            return request_serializer.data
        else:
            request_serializer = self.RequestSerializer(
                data=request_data, many=self.many_request_data
            )
            self._request_serializer = request_serializer
            is_valid_request = request_serializer.is_valid()
            if not is_valid_request:
                logger.error(
                    f"Resource[{self.get_resource_name()}] 请求参数格式错误：%s",
                    format_serializer_errors(request_serializer),
                )
                raise ResourceException(
                    _("Resource[{}] 请求参数格式错误：{}").format(
                        self.get_resource_name(),
                        format_serializer_errors(request_serializer),
                    )
                )
            return request_serializer.validated_data

    def validate_response_data(self, response_data):
        """
        校验返回数据
        """
        self._response_serializer = None
        if not self.ResponseSerializer:
            return response_data

        # model类型的数据需要特殊处理
        if isinstance(response_data, models.Model | models.QuerySet):
            response_serializer = self.ResponseSerializer(
                response_data, many=self.many_response_data
            )
            self._response_serializer = response_serializer
            return response_serializer.data
        else:
            response_serializer = self.ResponseSerializer(
                data=response_data, many=self.many_response_data
            )
            self._response_serializer = response_serializer
            is_valid_response = response_serializer.is_valid()
            if not is_valid_response:
                raise ResourceException(
                    _("Resource[{}] 返回参数格式错误：{}").format(
                        self.get_resource_name(),
                        format_serializer_errors(response_serializer),
                    )
                )
            return response_serializer.validated_data

    def request(self, request_data=None, **kwargs):
        """
        执行请求，并对请求数据和返回数据进行数据校验
        """
        with tracer.start_as_current_span(
            self.get_resource_name(), record_exception=False
        ) as span:
            try:
                request_data = request_data or kwargs
                validated_request_data = self.validate_request_data(request_data)
                response_data = self.perform_request(validated_request_data)

                # 如果返回的是 Django 响应对象（HttpResponse、render 等），直接返回，跳过响应数据校验
                if isinstance(response_data, HttpResponseBase):
                    return response_data

                validated_response_data = self.validate_response_data(response_data)
                return validated_response_data
            except Exception as exc:  # pylint: disable=broad-except
                # Record the exception as an event
                span.record_exception(exc)

                # Set status in case exception was raised
                span.set_status(
                    Status(
                        status_code=StatusCode.ERROR,
                        description=f"{type(exc).__name__}: {exc}",
                    )
                )
                raise

    def bulk_request(self, request_data_iterable=None, ignore_exceptions=False):
        """
        基于多线程的批量并发请求
        """
        if not isinstance(request_data_iterable, list | tuple):
            raise TypeError("'request_data_iterable' object is not iterable")

        pool = ThreadPool()
        futures = []
        for request_data in request_data_iterable:
            futures.append(pool.apply_async(self.request, args=(request_data,)))

        pool.close()
        pool.join()

        results = []
        exceptions = []
        for future in futures:
            try:
                results.append(future.get())
            except Exception as e:
                # 判断是否忽略错误
                if not ignore_exceptions:
                    raise e
                exceptions.append(e)
                results.append(None)

        # 如果全部报错，则必须抛出错误
        if exceptions and len(exceptions) == len(futures):
            raise exceptions[0]

        return results

    def update_state(self, state, message=None, data=None):
        """
        更新执行状态
        """
        state_message = f"Async resource task running - {self.get_resource_name()} [state=`{state}` message=`{message}` data=`{data}`]"
        logger.info(state_message)

        if not self._task_manager:
            return

        meta = {
            "message": message,
            "data": data,
        }
        self._task_manager.update_state(state=state, meta=meta)

    def delay(self, request_data=None, **kwargs):
        """
        执行celery异步任务
        """
        request_data = request_data or kwargs
        return self.apply_async(request_data)

    def apply_async(self, request_data, **kwargs):
        """
        执行celery异步任务（高级）
        """
        async_task = run_perform_request.apply_async(
            args=(self, get_request_username(), request_data), **kwargs
        )
        return {"task_id": async_task.id}

    @classmethod
    def generate_doc(cls):
        request_serializer_class, response_serializer_class = (
            cls._search_serializer_class()
        )
        request_params = get_serializer_fields(request_serializer_class)
        response_params = get_serializer_fields(response_serializer_class)

        return {
            "request_params": render_schema_structured(request_params),
            "response_params": render_schema_structured(
                response_params, using_source=True
            ),
        }
