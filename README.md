# DRF Resource

> 基于 Django REST Framework 的声明式资源框架，从腾讯蓝鲸监控平台 (BlueKing Monitor) 改造而来

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📖 简介

`drf_resource` 是一个基于 Django REST Framework 的轻量级声明式资源框架，从 [腾讯蓝鲸监控平台](https://github.com/TencentBlueKing/bk-monitor) 提取并重构，提供简洁高效的资源化 API 开发范式。

**解决的问题**：传统 DRF ViewSet 将业务逻辑与 HTTP 层耦合，难以复用；缺乏统一的业务逻辑原子化封装；缺少开箱即用的批量请求、异步任务、自动文档等能力。

**核心差异**：与 DRF 原生 ViewSet 相比，业务逻辑抽离为可独立调用的 Resource，支持跨模块复用；与纯函数式服务层相比，提供声明式校验、序列化、缓存、文档生成等完整生命周期。

## ✨ 核心特性

- **声明式 API 开发**：继承 Resource 基类，定义业务逻辑即可自动获得请求/响应校验、文档生成
- **自动序列化器发现**：遵循命名约定自动绑定 RequestSerializer 和 ResponseSerializer
- **多层级资源**：`Resource` / `CacheResource` / `APIResource` / `APICacheResource`
- **批量与异步**：`bulk_request` 并发执行、`delay` / `apply_async` Celery 任务
- **自动发现**：扫描 `resource`、`adapter`、`api` 模块并自动注册全局入口
- **ViewSet 集成**：`ResourceViewSet` 将 Resource 快速暴露为 RESTful API
- **API 文档**：基于 drf-spectacular 自动生成 OpenAPI 文档（Swagger UI / ReDoc）

## 🚀 快速开始

### 安装

```bash
pip install drf-resource
# → Successfully installed drf-resource-0.1.0
```

### 配置

在 Django `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'drf_resource',
]

DRF_RESOURCE = {
    'HTTP_TIMEOUT': 60,
    'HTTP_VERIFY_SSL': False,
}
```

### 定义 Resource

```python
from rest_framework import serializers
from drf_resource.resources.base import Resource

class UserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()

class UserResource(Resource):
    RequestSerializer = UserRequestSerializer
    ResponseSerializer = UserResponseSerializer

    def perform_request(self, validated_request_data):
        return {'id': validated_request_data['user_id'], 'username': 'john'}
```

### 调用 Resource

```python
from drf_resource import resource

result = resource.users.user({'user_id': 123})
# → {'id': 123, 'username': 'john'}

results = resource.users.user.bulk_request([{'user_id': 1}, {'user_id': 2}])
# → [{'id': 1, 'username': 'john'}, {'id': 2, 'username': 'jane'}]
```

### 暴露为 REST API

```python
from rest_framework.routers import DefaultRouter
from drf_resource.views.viewsets import ResourceViewSet, ResourceRoute
from drf_resource import resource

class UserViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute(method='GET', resource_class=resource.users.user, endpoint='detail', pk_field='id'),
    ]

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = router.urls
```

访问 `GET /api/users/1/` 即可调用 UserResource。

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [配置参考](docs/configuration.md) | `DRF_RESOURCE` 全部配置项的类型、默认值与使用场景 |
| [API 参考](docs/Resource框架自动发现与使用.md) | 自动发现机制、扫描规则、全局入口使用 |
| [使用技巧](docs/Resource框架使用小技巧.md) | 线程安全、批量请求、异步任务、调试技巧 |

## 📄 许可证

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [腾讯蓝鲸监控平台](https://github.com/TencentBlueKing/bk-monitor)
- [httpflex - HTTP 客户端库](https://github.com/HACK-WU/httpflex-py)
- [Django REST Framework](https://www.django-rest-framework.org/)
