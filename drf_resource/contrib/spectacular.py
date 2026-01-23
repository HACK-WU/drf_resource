"""
drf-spectacular 扩展模块

为 ResourceViewSet 提供 OpenAPI 3.0 schema 生成支持。

使用方法
--------
在项目的 settings.py 中配置：

```python
INSTALLED_APPS = [
    # ...
    "drf_spectacular",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_resource.contrib.spectacular.FaultTolerantAutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Your API",
    "VERSION": "1.0.0",
    "DESCRIPTION": "API 文档",
    "SERVE_INCLUDE_SCHEMA": False,
    # 可选：启用 ResourceViewSet 预处理钩子
    "PREPROCESSING_HOOKS": [
        "drf_resource.contrib.spectacular.preprocess_resource_routes",
    ],
}
```

在 urls.py 中配置文档路由：

```python
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # OpenAPI Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc（可选）
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
```
"""

import logging

from rest_framework.serializers import Serializer

logger = logging.getLogger(__name__)


# ============================================================================
# 容错 AutoSchema 类
# ============================================================================

# 尝试导入 drf-spectacular 的 AutoSchema 作为基类
try:
    from drf_spectacular.openapi import AutoSchema as _BaseAutoSchema

    _HAS_SPECTACULAR = True
except ImportError:
    from rest_framework.schemas.openapi import AutoSchema as _BaseAutoSchema

    _HAS_SPECTACULAR = False


class FaultTolerantAutoSchema(_BaseAutoSchema):
    """
    容错的 AutoSchema 类

    当生成 API 文档时遇到错误（如自定义 permission 类访问不存在的 request 属性），
    会记录警告日志并跳过该端点，而不是抛出异常导致整个文档生成失败。

    使用方法：
    在 REST_FRAMEWORK 配置中设置：
    'DEFAULT_SCHEMA_CLASS': 'drf_resource.contrib.spectacular.FaultTolerantAutoSchema'
    """

    def get_operation(self, path, path_regex, path_prefix, method, registry):
        """
        重写 get_operation 方法，捕获异常并跳过有问题的端点
        """
        try:
            result = super().get_operation(
                path, path_regex, path_prefix, method, registry
            )
            if result:
                logger.debug(f"[drf-spectacular] 成功生成 schema: {method} {path}")
            return result
        except Exception as e:
            logger.warning(
                f"[drf-spectacular] 跳过端点 {method} {path}，生成 schema 时发生错误: {type(e).__name__}: {e}"
            )
            # 返回 None 表示跳过该端点
            return None


# ============================================================================
# Schema 辅助函数
# ============================================================================


def get_resource_schema(view_cls, method: str, action: str):
    """
    从 ResourceViewSet 的 resource_routes 中提取对应 action 的 schema 信息

    Args:
        view_cls: ViewSet 类
        method: HTTP 方法 (GET, POST, PUT, PATCH, DELETE)
        action: DRF action 名称 (list, create, retrieve, update, destroy, 或自定义 endpoint)

    Returns:
        dict: 包含 request, responses, description 的 schema 配置
        None: 如果未找到匹配的路由
    """
    resource_routes = getattr(view_cls, "resource_routes", [])

    # 空 endpoint 对应的标准方法映射
    empty_endpoint_methods = {
        "GET": "list",
        "POST": "create",
        "PUT": "update",
        "PATCH": "partial_update",
        "DELETE": "destroy",
    }

    for route in resource_routes:
        # 确定当前路由对应的 action 名称
        if route.endpoint:
            route_action = route.endpoint
        else:
            # 空 endpoint 映射到标准方法
            if route.pk_field and route.method == "GET":
                route_action = "retrieve"
            else:
                route_action = empty_endpoint_methods.get(route.method, "")

        # 检查是否匹配
        if route_action == action and route.method == method.upper():
            request_serializer = route.resource_class.RequestSerializer or Serializer
            response_serializer = route.resource_class.ResponseSerializer or Serializer
            # 强制转换为字符串，避免 lazy translation 对象导致 YAML 序列化失败
            description = (
                str(route.resource_class.__doc__).strip()
                if route.resource_class.__doc__
                else ""
            )

            return {
                "request": request_serializer,
                "responses": {200: response_serializer},
                "description": description,
            }

    return None


def preprocess_resource_routes(endpoints, **kwargs):
    """
    drf-spectacular 预处理钩子

    为 ResourceViewSet 的动态端点添加 schema 信息。
    在 SPECTACULAR_SETTINGS['PREPROCESSING_HOOKS'] 中配置此函数。

    Args:
        endpoints: 端点列表 [(path, path_regex, method, callback), ...]
        **kwargs: 其他参数

    Returns:
        处理后的端点列表
    """
    try:
        from drf_spectacular.utils import extend_schema
    except ImportError:
        # drf-spectacular 未安装，直接返回原始端点
        return endpoints

    from drf_resource.viewsets import ResourceViewSet

    processed = []
    for endpoint_tuple in endpoints:
        path, path_regex, method, callback = endpoint_tuple
        view_cls = getattr(callback, "cls", None)

        if view_cls and issubclass(view_cls, ResourceViewSet):
            # 获取 action 名称
            actions = getattr(callback, "actions", {})
            action = actions.get(method.lower(), "")

            # 获取 schema 信息
            schema_info = get_resource_schema(view_cls, method, action)

            if schema_info:
                # 应用 extend_schema 装饰器
                decorated_callback = extend_schema(
                    request=schema_info["request"],
                    responses=schema_info["responses"],
                    description=schema_info["description"],
                )(callback)
                processed.append((path, path_regex, method, decorated_callback))
                continue

        processed.append(endpoint_tuple)

    return processed


def generate_resource_schema_decorator(resource_route):
    """
    为单个 ResourceRoute 生成 extend_schema 装饰器

    可用于在 ResourceViewSet.generate_endpoint 中动态生成文档装饰器。

    Args:
        resource_route: ResourceRoute 实例

    Returns:
        extend_schema 装饰器，或空装饰器（如果 drf-spectacular 未安装）
    """
    try:
        from drf_spectacular.utils import extend_schema
    except ImportError:
        return lambda f: f

    request_serializer = resource_route.resource_class.RequestSerializer or Serializer
    response_serializer = resource_route.resource_class.ResponseSerializer or Serializer
    # 强制转换为字符串，避免 lazy translation 对象导致 YAML 序列化失败
    description = (
        str(resource_route.resource_class.__doc__).strip()
        if resource_route.resource_class.__doc__
        else ""
    )

    # GET 请求：将 serializer 作为 query parameters
    # 其他请求：将 serializer 作为 request body
    if resource_route.method == "GET":
        return extend_schema(
            parameters=[request_serializer],
            responses={200: response_serializer},
            description=description,
        )
    else:
        return extend_schema(
            request=request_serializer,
            responses={200: response_serializer},
            description=description,
        )


# ============================================================================
# 标签过滤 Schema 生成器
# ============================================================================

try:
    from drf_spectacular.generators import SchemaGenerator

    _HAS_SCHEMA_GENERATOR = True
except ImportError:
    SchemaGenerator = object
    _HAS_SCHEMA_GENERATOR = False


class FilterableSchemaGenerator(SchemaGenerator):
    """
    支持按标签（Tag）过滤的 Schema 生成器

    允许通过 tags 参数只生成包含指定标签的 API 端点的 schema，
    从而实现按需加载 API 文档，减少浏览器内存占用。

    使用方法：
    - 设置 tags 属性为要过滤的标签列表
    - 调用 get_schema() 生成过滤后的 schema
    """

    def __init__(self, *args, tags=None, **kwargs):
        """
        初始化 Schema 生成器

        Args:
            tags: 要过滤的标签列表，如 ['user', 'auth']。
                  如果为 None 或空列表，则返回完整 schema。
        """
        super().__init__(*args, **kwargs)
        self.filter_tags = tags or []

    def parse(self, request, public):
        """
        重写 parse 方法，实现标签过滤

        Returns:
            过滤后的 paths 字典
        """
        # 调用父类的 parse 方法获取完整的 paths
        result = super().parse(request, public)

        # 如果没有指定过滤标签，返回完整结果
        if not self.filter_tags:
            return result

        # 过滤 paths，只保留包含指定标签的端点
        filtered_paths = {}
        for path, path_item in result.items():
            filtered_operations = {}
            for method, operation in path_item.items():
                # 获取该操作的标签
                operation_tags = operation.get("tags", [])
                # 检查是否有任何标签匹配过滤条件
                if any(tag in self.filter_tags for tag in operation_tags):
                    filtered_operations[method] = operation

            # 只有当路径下还有操作时才添加
            if filtered_operations:
                filtered_paths[path] = filtered_operations

        return filtered_paths

    def get_schema(self, request=None, public=False):
        """
        重写 get_schema 方法，过滤 tags 列表

        确保返回的 schema 中的 tags 列表也只包含被使用的标签。
        """
        schema = super().get_schema(request=request, public=public)

        # 如果没有过滤标签，返回完整 schema
        if not self.filter_tags:
            return schema

        # 过滤 schema 中的 tags 列表
        if "tags" in schema:
            schema["tags"] = [
                tag for tag in schema["tags"] if tag.get("name") in self.filter_tags
            ]

        return schema


# ============================================================================
# Schema 视图与缓存
# ============================================================================

from hashlib import md5
from django.conf import settings
from django.core.cache import cache as django_cache

# 默认缓存超时时间（秒）
DEFAULT_SCHEMA_CACHE_TIMEOUT = 3600  # 1小时


def get_schema_cache_timeout():
    """获取 schema 缓存超时时间"""
    drf_resource_settings = getattr(settings, "DRF_RESOURCE", {})
    return drf_resource_settings.get(
        "SCHEMA_CACHE_TIMEOUT", DEFAULT_SCHEMA_CACHE_TIMEOUT
    )


def get_docs_tag_threshold():
    """获取分组接口数量警告阈值"""
    drf_resource_settings = getattr(settings, "DRF_RESOURCE", {})
    return drf_resource_settings.get("DOCS_TAG_THRESHOLD", 100)


def generate_cache_key(prefix, *args):
    """
    生成缓存 key

    Args:
        prefix: 缓存 key 前缀
        *args: 用于生成唯一 key 的参数

    Returns:
        缓存 key 字符串
    """
    key_data = ":".join(str(arg) for arg in args if arg)
    hash_suffix = md5(key_data.encode()).hexdigest()[:12]
    return f"{prefix}:{hash_suffix}"


try:
    from drf_spectacular.views import SpectacularAPIView

    _HAS_SPECTACULAR_VIEWS = True
except ImportError:
    SpectacularAPIView = object
    _HAS_SPECTACULAR_VIEWS = False


class FilterableSpectacularAPIView(SpectacularAPIView):
    """
    支持标签过滤和缓存的 Schema API 视图

    查询参数：
    - tags: 逗号分隔的标签列表，如 ?tags=user,auth
    - refresh: 设置为 1 时强制刷新缓存，如 ?refresh=1
    - format: 输出格式 (json/yaml)

    示例：
    - /schema/ - 返回完整 schema（带缓存）
    - /schema/?tags=user - 返回 user 标签的 schema
    - /schema/?tags=user,auth - 返回 user 和 auth 标签的 schema
    - /schema/?refresh=1 - 强制刷新缓存
    """

    def _get_schema_generator_class(self):
        """返回自定义的 Schema 生成器类"""
        return FilterableSchemaGenerator

    def _get_tags_from_request(self, request):
        """从请求中提取标签列表"""
        tags_param = request.query_params.get("tags", "")
        if tags_param:
            return [tag.strip() for tag in tags_param.split(",") if tag.strip()]
        return []

    def _should_refresh_cache(self, request):
        """检查是否需要强制刷新缓存"""
        return request.query_params.get("refresh", "") == "1"

    def _get_cache_key(self, request, tags):
        """生成缓存 key"""
        tags_str = ",".join(sorted(tags)) if tags else "all"
        format_type = request.query_params.get("format", "json")
        return generate_cache_key("drf_resource:schema", tags_str, format_type)

    def _get_schema_response(self, request):
        """
        重写父类方法，添加标签过滤和缓存支持
        """
        from rest_framework.response import Response

        tags = self._get_tags_from_request(request)
        should_refresh = self._should_refresh_cache(request)
        cache_key = self._get_cache_key(request, tags)
        cache_timeout = get_schema_cache_timeout()

        # 检查缓存（除非强制刷新）
        if not should_refresh and cache_timeout > 0:
            cached_schema = django_cache.get(cache_key)
            if cached_schema is not None:
                return Response(data=cached_schema)

        # 使用自定义的 FilterableSchemaGenerator
        generator_class = self._get_schema_generator_class()
        generator = generator_class(
            urlconf=self.urlconf,
            api_version=self.api_version,
            patterns=self.patterns,
            tags=tags,  # 传递标签过滤参数
        )

        schema = generator.get_schema(request=request, public=self.serve_public)

        # 缓存结果
        if cache_timeout > 0:
            django_cache.set(cache_key, schema, cache_timeout)

        return Response(data=schema)


# ============================================================================
# API 标签统计服务
# ============================================================================


def get_all_api_tags(request=None):
    """
    获取所有已注册 API 的标签信息

    Returns:
        dict: {tag_name: endpoint_count} 的字典
    """
    from drf_spectacular.generators import SchemaGenerator

    # 尝试从缓存获取
    cache_key = "drf_resource:api_tags_summary"
    cache_timeout = get_schema_cache_timeout()

    cached_result = django_cache.get(cache_key)
    if cached_result is not None:
        logger.debug(
            f"[drf-spectacular] 从缓存获取 API 标签，共 {len(cached_result)} 个标签"
        )
        return cached_result

    # 生成 schema 以获取所有端点信息
    logger.info("[drf-spectacular] 开始生成 API schema...")
    generator = SchemaGenerator()
    try:
        # 不传递 request 参数，避免 WSGIRequest 缺少 auth 属性的问题
        # drf-spectacular 会自动创建 mock request
        schema = generator.get_schema(request=None, public=True)
    except Exception as e:
        logger.error(
            f"[drf-spectacular] 获取 API 标签时发生错误: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return []

    # 统计每个标签的接口数量
    tags_count = {}
    paths = schema.get("paths", {})
    logger.info(f"[drf-spectacular] schema 生成完成，共 {len(paths)} 个路径")

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if isinstance(operation, dict):
                operation_tags = operation.get("tags", ["未分类"])
                for tag in operation_tags:
                    tags_count[tag] = tags_count.get(tag, 0) + 1

    # 获取 schema 中定义的标签描述
    schema_tags = {
        tag.get("name"): tag.get("description", "") for tag in schema.get("tags", [])
    }

    # 合并结果
    result = []
    for tag_name, count in sorted(tags_count.items()):
        result.append(
            {
                "name": tag_name,
                "description": schema_tags.get(tag_name, ""),
                "count": count,
                "warning": count > get_docs_tag_threshold(),
            }
        )

    logger.info(f"[drf-spectacular] 统计完成，共 {len(result)} 个 API 标签")

    # 缓存结果（只缓存非空结果）
    if cache_timeout > 0 and result:
        django_cache.set(cache_key, result, cache_timeout)

    return result


def clear_schema_cache():
    """
    清除所有 schema 相关的缓存

    可在接口变更后调用此函数刷新缓存
    """
    # 清除标签统计缓存
    django_cache.delete("drf_resource:api_tags_summary")
    # 注意：由于 schema 缓存使用了 hash key，这里无法清除所有 schema 缓存
    # 建议在 settings 中配置合理的缓存超时时间
    logger.info("[drf-spectacular] Schema 缓存已清除")


# ============================================================================
# 文档视图
# ============================================================================

from django.views.generic import TemplateView
from django.http import JsonResponse


class DocsIndexView(TemplateView):
    """
    分组文档入口页面视图

    展示所有可用的 API 分组（标签），让用户选择要查看的分组，
    避免一次性加载所有 API 文档导致浏览器卡顿。
    """

    template_name = "spectacular/docs_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 不传递 request，避免 WSGIRequest 缺少 auth 属性的问题
        context["tags"] = get_all_api_tags()
        context["threshold"] = get_docs_tag_threshold()
        return context


try:
    from drf_spectacular.views import SpectacularSwaggerView

    _HAS_SWAGGER_VIEW = True
except ImportError:
    SpectacularSwaggerView = TemplateView
    _HAS_SWAGGER_VIEW = False


class FilterableSwaggerView(SpectacularSwaggerView):
    """
    支持标签过滤的 Swagger UI 视图

    从 URL 查询参数获取 tags，并将其传递给 schema URL，
    实现按分组展示 API 文档。

    示例：
    - /docs/swagger/ - 完整文档（但会显示分组选择提示）
    - /docs/swagger/?tags=user - 只显示 user 分组的文档
    """

    template_name = "spectacular/swagger.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = self.request.GET.get("tags", "")

        # 构建带标签过滤的 schema URL
        schema_url = self.url or context.get("url", "/schema/")
        if tags:
            separator = "&" if "?" in schema_url else "?"
            schema_url = f"{schema_url}{separator}tags={tags}"

        context["schema_url"] = schema_url
        context["tags"] = tags
        return context


class DocsLiteView(TemplateView):
    """
    轻量级 API 文档列表视图

    只展示 API 的基本信息（路径、方法、描述、标签），
    不加载完整的 serializer schema，适合接口数量庞大的项目快速浏览。
    """

    template_name = "spectacular/docs_lite.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 获取标签过滤参数
        tags_param = self.request.GET.get("tags", "")
        filter_tags = (
            [t.strip() for t in tags_param.split(",") if t.strip()]
            if tags_param
            else []
        )

        # 获取 API 列表
        context["apis"] = self._get_api_list(filter_tags)
        # 不传递 request，避免 WSGIRequest 缺少 auth 属性的问题
        context["tags"] = get_all_api_tags()
        context["filter_tags"] = filter_tags
        return context

    def _get_api_list(self, filter_tags=None):
        """
        获取简化的 API 列表

        Args:
            filter_tags: 要过滤的标签列表

        Returns:
            按标签分组的 API 列表
        """
        from drf_spectacular.generators import SchemaGenerator

        try:
            generator = SchemaGenerator()
            # 不传递 request 参数，避免 WSGIRequest 缺少 auth 属性的问题
            schema = generator.get_schema(request=None, public=True)
        except Exception as e:
            logger.warning(f"[drf-spectacular] 获取 API 列表时发生错误: {e}")
            return {}

        # 按标签分组
        apis_by_tag = {}
        paths = schema.get("paths", {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict):
                    continue

                operation_tags = operation.get("tags", ["未分类"])

                # 如果指定了过滤标签，检查是否匹配
                if filter_tags and not any(
                    tag in filter_tags for tag in operation_tags
                ):
                    continue

                api_info = {
                    "path": path,
                    "method": method.upper(),
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "operation_id": operation.get("operationId", ""),
                    "deprecated": operation.get("deprecated", False),
                }

                for tag in operation_tags:
                    if tag not in apis_by_tag:
                        apis_by_tag[tag] = []
                    apis_by_tag[tag].append(api_info)

        return dict(sorted(apis_by_tag.items()))


class ApiTagsView(TemplateView):
    """
    API 标签统计接口

    返回所有可用标签及其接口数量的 JSON 数据
    """

    def get(self, request, *args, **kwargs):
        # 不传递 request，避免 WSGIRequest 缺少 auth 属性的问题
        tags = get_all_api_tags()
        return JsonResponse({"tags": tags, "threshold": get_docs_tag_threshold()})
