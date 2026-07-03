# S-03：drf_resource 集成设计

> 父文档：[DESIGN.md](DESIGN.md) | 共享术语：Resource、ResourceViewSet、ResourceRouter

## 术语

| 术语 | 定义 |
|------|------|
| Resource | drf_resource 框架的核心抽象，通过 `perform_request()` 封装业务逻辑 |
| ResourceViewSet | 基于 Resource 的 ViewSet，通过 `ResourceRoute` 声明式配置路由 |
| ResourceRouter | 批量注册 ViewSet 的 Router |

## 现状（AS-IS）

drf_resource 在 `/root/drf_resource/` 提供完整框架代码，但用户需要手动创建 Django 项目并集成。

## 方案（TO-BE）

### 1. urls.py — URL 路由

文件：[`{{cookiecutter.project_name}}/{{cookiecutter.project_name}}/urls.py`](file:///urls.py)

```python
"""URL 路由配置"""
from django.contrib import admin
from django.urls import path, include
from drf_resource.views.routers import ResourceRouter
from {{ cookiecutter.project_name }}.apps.example.viewsets import ExampleViewSet

router = ResourceRouter()
router.register("example", ExampleViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    {% if cookiecutter.enable_api_docs == "yes" %}
    # API 文档
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    {% endif %}
]

{% if cookiecutter.enable_api_docs == "yes" %}
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
{% endif %}
```

### 2. 示例 App — apps/example/

设计目标：演示 drf_resource 的标准用法（Resource + ViewSet + Serializer 完整链路）。

#### serializers.py

文件：[`{{cookiecutter.project_name}}/apps/example/serializers.py`](file:///apps/example/serializers.py)

```python
"""示例 Serializer"""
from rest_framework import serializers

class ExampleRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, help_text="名称")

class ExampleResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID")
    name = serializers.CharField(help_text="名称")
    message = serializers.CharField(help_text="响应消息")
```

#### resources.py

文件：[`{{cookiecutter.project_name}}/apps/example/resources.py`](file:///apps/example/resources.py)

```python
"""示例 Resource"""
from drf_resource.resources.base import Resource
from {{ cookiecutter.project_name }}.apps.example.serializers import (
    ExampleRequestSerializer,
    ExampleResponseSerializer,
)

class ExampleResource(Resource):
    """
    示例资源 - 演示 drf_resource 的基本用法

    接收一个 name 参数，返回一条问候消息。
    """
    RequestSerializer = ExampleRequestSerializer
    ResponseSerializer = ExampleResponseSerializer

    def perform_request(self, validated_request_data):
        name = validated_request_data["name"]
        return {
            "id": 1,
            "name": name,
            "message": f"Hello, {name}! This is powered by drf_resource.",
        }
```

#### viewsets.py

文件：[`{{cookiecutter.project_name}}/apps/example/viewsets.py`](file:///apps/example/viewsets.py)

```python
"""示例 ViewSet"""
from drf_resource.views.viewsets import ResourceViewSet, ResourceRoute
from {{ cookiecutter.project_name }}.apps.example.resources import ExampleResource

class ExampleViewSet(ResourceViewSet):
    """
    示例接口

    提供 GET /api/example/ 端点，返回问候消息。
    """
    resource_routes = [
        ResourceRoute(
            method="GET",
            resource_class=ExampleResource,
        ),
    ]
```

### API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/example/?name=xxx` | 返回问候消息 |

### Demo 返回示例

```json
{
    "result": true,
    "code": 200,
    "data": {
        "id": 1,
        "name": "World",
        "message": "Hello, World! This is powered by drf_resource."
    },
    "message": "success"
}
```
