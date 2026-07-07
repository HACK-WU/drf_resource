"""
drf-spectacular 接口文档 URL 配置

使用方法
--------
在项目的 urls.py 中添加一行即可完成所有接口文档路由的配置：

```python
from django.urls import include, path

urlpatterns = [
    # ... 其他 URL ...

    # 接口文档（一行导入所有文档路由）
    path("", include("drf_resource.contrib.urls")),

    # API Explorer（第三方 API 在线调试）
    # 需要单独配置，见 API Explorer 文档
]
```

路径前缀自定义
--------------
如果 ``docs/``、``schema/``、``redoc/`` 等路径与项目中已有路由冲突，
可以通过 ``include`` 时指定前缀来避免：

```python
# 添加 api/ 前缀，所有文档路由变为 /api/docs/、/api/schema/ 等
path("api/", include("drf_resource.contrib.urls")),
```

URL 命名空间
------------
本模块使用 ``drf_resource_docs`` 命名空间，避免与项目中已有 URL name 冲突。
使用 ``reverse`` 时需带上命名空间：

```python
from django.urls import reverse

schema_url = reverse("drf_resource_docs:schema")
swagger_url = reverse("drf_resource_docs:swagger-ui")
```

提供的路由
----------
- ``schema/`` — OpenAPI Schema（支持标签过滤和缓存）
- ``docs/`` — API 文档首页
- ``docs/swagger/`` — Swagger UI（支持标签过滤）
- ``docs/tags/`` — API 标签统计接口
- ``docs/clear-cache/`` — 清除 Schema 缓存（本地开发用）
- ``redoc/`` — ReDoc 文档（支持缓存和标签过滤）

查询参数
--------
- ``tags`` — 逗号分隔的标签列表，如 ``?tags=user,auth``
- ``prefix`` — 路径前缀过滤，如 ``?prefix=/api/v1``
- ``refresh`` — 设置为 1 时强制刷新缓存，如 ``?refresh=1``
- ``format`` — 输出格式 (json/yaml)

依赖说明
--------
本模块依赖 ``drf-spectacular`` 库。如果未安装，所有文档路由将返回
友好的安装提示（HTTP 501），不会影响项目正常运行。
请通过 ``pip install drf-spectacular`` 安装。
"""

from django.http import JsonResponse
from django.urls import path

from .spectacular import (
    _HAS_REDOC_VIEW,
    _HAS_SPECTACULAR_VIEWS,
    _HAS_SWAGGER_VIEW,
    ApiDocsView,
    ApiTagsView,
    FilterableSpectacularAPIView,
    FilterableSpectacularRedocView,
    FilterableSwaggerView,
    clear_schema_cache,
)

#: URL 命名空间，避免与项目中已有 URL name 冲突
#: 使用时需带命名空间：reverse("drf_resource_docs:schema")
app_name = "drf_resource_docs"


def clear_cache_view(request):
    """清除 schema 缓存的调试端点（本地开发用）"""
    clear_schema_cache()
    return JsonResponse(
        {"success": True, "message": "Schema 缓存已清除，请刷新页面"}
    )


def _drf_spectacular_not_installed_view(request):
    """drf-spectacular 未安装时的友好提示"""
    return JsonResponse(
        {
            "error": "drf-spectacular is not installed",
            "message": "请运行 pip install drf-spectacular 安装后重试",
        },
        status=501,
    )


# 根据 drf-spectacular 安装状态选择视图
# 未安装时使用友好提示视图，避免访问时报错
_schema_view = (
    FilterableSpectacularAPIView.as_view()
    if _HAS_SPECTACULAR_VIEWS
    else _drf_spectacular_not_installed_view
)
_swagger_view = (
    FilterableSwaggerView.as_view(url_name="drf_resource_docs:schema")
    if _HAS_SWAGGER_VIEW
    else _drf_spectacular_not_installed_view
)
_redoc_view = (
    FilterableSpectacularRedocView.as_view(url_name="drf_resource_docs:schema")
    if _HAS_REDOC_VIEW
    else _drf_spectacular_not_installed_view
)


urlpatterns = [
    # OpenAPI Schema（支持标签过滤和缓存）
    path("schema/", _schema_view, name="schema"),
    # Swagger UI（支持标签过滤）
    path("docs/swagger/", _swagger_view, name="swagger-ui"),
    # API 标签统计接口
    path("docs/tags/", ApiTagsView.as_view(), name="api-tags"),
    # API 文档页面
    path("docs/", ApiDocsView.as_view(), name="api-docs"),
    # ReDoc（支持缓存和标签过滤）
    path("redoc/", _redoc_view, name="redoc"),
    # 调试：清除缓存（本地开发用）
    path("docs/clear-cache/", clear_cache_view, name="clear-cache"),
]
