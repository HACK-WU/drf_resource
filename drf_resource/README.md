# DRF Resource

> 基于 Django REST Framework 的声明式资源框架，从腾讯蓝鲸监控平台 (BlueKing Monitor) 改造而来

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📖 简介

`drf_resource` 是一个基于 Django REST Framework 的轻量级声明式资源框架，通过声明式的方式简化 API 开发。该项目从 [腾讯蓝鲸监控平台 (BlueKing Monitor)](https://github.com/TencentBlueKing/bk-monitor) 中提取并重构，旨在提供一套简洁、高效的资源化 API 开发范式。

### 设计理念

DRF Resource 将业务逻辑封装为独立的 **Resource** 单元，每个 Resource 负责处理输入数据并返回处理结果。通过声明式的定义方式，配合自动发现机制，实现了业务逻辑的原子化、组件化和可复用性。

## ⚠️ 项目状态

> **注意**：drf_resource 的基本功能已经完成，但目前仍处于迭代和测试阶段，不建议用于生产环境。
>
> 如果您对该项目感兴趣，欢迎进行体验和测试，我们非常期待您的反馈和建议！在您使用过程中如果遇到任何问题，请随时通过 Issue 或 Pull Request 与我们联系。

## ✨ 核心特性

- **声明式 API 开发**：通过继承 Resource 基类，只需定义业务逻辑即可自动获得请求/响应校验、文档生成等功能
- **自动序列化器发现**：遵循命名约定自动查找并绑定 RequestSerializer 和 ResponseSerializer
- **多层级资源支持**：
  - `Resource`: 基础资源类
  - `CacheResource`: 带缓存能力的资源
  - `APIResource`: HTTP API 客户端（基于 httpflex 重构，功能更强大）
  - `APICacheResource`: 带缓存的 HTTP API 客户端
- **自动发现机制**：自动发现项目中的 `resource`、`adapter` 和 `api` 模块
- **批量请求支持**：基于多线程的批量并发请求
- **异步任务支持**：集成 Celery，支持异步任务执行
- **ViewSet 集成**：通过 `ResourceViewSet` 将 Resource 快速暴露为 RESTful API
- **多平台适配**：通过 adapter 机制支持多版本/多平台的差异化逻辑
- **OpenTelemetry 支持**：可选的分布式追踪能力
- **API Explorer**：内置 API 调试界面，方便接口测试

## 📦 项目来源与致谢

### 项目来源

本项目从 [腾讯蓝鲸监控平台 (BlueKing Monitor)](https://github.com/TencentBlueKing/bk-monitor) 中提取并独立改造而成。

**BlueKing Monitor** 是蓝鲸智云官方推出的一款监控平台产品，除了具有丰富的数据采集能力，大规模的数据处理能力，简单易用，还提供更多的平台扩展能力。依托于蓝鲸 PaaS，有别于传统的 CS 结构，在整个蓝鲸生态中可以形成监控的闭环能力。

`drf_resource` 框架最初于 2019 年底在蓝鲸监控平台中实现，用于简化 SaaS 和后台 API 模块的 API 开发。在监控平台项目中，基于 DRF 的 ModelView 设计理念，实现了基于业务逻辑单元的 ViewSet 封装，配合自动发现能力，让代码逻辑实现基于 Resource 原子的组装和复用。

### 致谢

- **腾讯蓝鲸团队**：感谢腾讯蓝鲸团队开源了 BlueKing Monitor 项目，为社区提供了优秀的监控平台解决方案
- **Django REST Framework**：本框架基于 DRF 构建，感谢 DRF 团队提供的优秀基础框架
- **httpflex**：感谢 [httpflex](https://github.com/HACK-WU/httpflex-py) 项目提供的强大 HTTP 客户端能力，为 APIResource 带来了质的飞跃
- **开源社区**：感谢所有为开源项目贡献代码、提供建议的开发者

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/HACK-WU/drf_resource.git
```

### 配置

在 Django 项目的 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'drf_resource',
]

# DRF Resource 配置（可选）
DRF_RESOURCE = {
    # 是否启用自动发现
    'AUTO_DISCOVERY': True,
    
    # 是否启用资源数据收集
    'RESOURCE_DATA_COLLECT_ENABLED': False,
    
    # 用户名字段
    'USERNAME_FIELD': 'username',
    
    # HTTP Resource 默认配置
    'HTTP_TIMEOUT': 60,
    'HTTP_VERIFY_SSL': False,
}
```

### 基本用法

#### 1. 定义 Resource

```python
from rest_framework import serializers
from drf_resource.base import Resource

# 定义请求序列化器
class UserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

# 定义响应序列化器（可选）
class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()

# 定义 Resource
class UserResource(Resource):
    RequestSerializer = UserRequestSerializer
    ResponseSerializer = UserResponseSerializer
    
    def perform_request(self, validated_request_data):
        user_id = validated_request_data['user_id']
        # 业务逻辑处理
        user = User.objects.get(id=user_id)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
```

#### 2. 使用 Resource

```python
# 直接调用
resource = UserResource()
result = resource.request({'user_id': 123})
# 返回: {'id': 123, 'username': 'john', 'email': 'john@example.com'}

# 批量请求
results = resource.bulk_request([
    {'user_id': 1},
    {'user_id': 2},
])
# 返回: [{'id': 1, ...}, {'id': 2, ...}]
```

#### 3. 暴露为 API

```python
from rest_framework.routers import DefaultRouter
from drf_resource.viewsets import ResourceViewSet, ResourceRoute

# 定义 ViewSet
class UserViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute(
            method='GET',
            resource_class=UserResource,
            endpoint='detail',
            pk_field='id',
        )
    ]

# 注册路由
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls
```

访问 `GET /api/users/1/` 即可调用 UserResource。

## 📚 详细使用指南

### Resource 基类

Resource 是 drf_resource 的核心基类，所有自定义资源都需要继承它。

#### 自动序列化器发现

如果遵循命名约定，可以省略手动指定序列化器：

```python
# resources.py
class UserResource(Resource):
    def perform_request(self, validated_request_data):
        # 会自动查找 UserRequestSerializer 和 UserResponseSerializer
        pass
```

#### 访问请求对象

在 ViewSet 中使用时，可以通过 `self._current_request` 访问请求对象：

```python
class UserResource(Resource):
    def perform_request(self, validated_request_data):
        user = self._current_request.user
        return {'username': user.username}
```

#### 返回 HttpResponse

`perform_request()` 可以直接返回 Django 响应对象：

```python
from django.shortcuts import render

class PageResource(Resource):
    def perform_request(self, validated_request_data):
        return render(self._current_request, 'template.html', context)
```

### CacheResource 缓存资源

为 Resource 添加缓存能力：

```python
from drf_resource.cache import CacheTypeItem
from drf_resource.contrib import CacheResource

class CachedUserResource(CacheResource):
    RequestSerializer = UserRequestSerializer
    ResponseSerializer = UserResponseSerializer
    
    # 配置缓存
    cache_type = CacheTypeItem(key="user_cache", timeout=60)  # 缓存 60 秒
    cache_user_related = True  # 缓存与用户关联
    cache_compress = True  # 使用压缩
    
    def perform_request(self, validated_request_data):
        # 业务逻辑
        pass
```

### APIResource HTTP 客户端

> 🎉 **重大更新**：APIResource 已经使用 [httpflex](https://github.com/HACK-WU/httpflex-py) 模块进行重构，极大增强了 HTTP 客户端能力！

[httpflex](https://github.com/HACK-WU/httpflex-py) 是一个功能强大的 HTTP 客户端库，为 APIResource 带来了以下增强特性：

- **更强大的请求构建能力**：支持更灵活的请求参数配置
- **更好的错误处理机制**：提供更完善的异常处理和重试策略
- **更高效的性能优化**：基于现代 HTTP 客户端的性能提升
- **更丰富的中间件支持**：可扩展的中间件机制
- **更完善的测试支持**：更好的 Mock 和测试工具

调用外部 HTTP API：

```python
from drf_resource.contrib import APIResource

class ExternalAPI(APIResource):
    base_url = "https://api.example.com"
    module_name = "example_service"
    action = "/api/v1/users/"
    method = "GET"
    
    class RequestSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True)
    
    def get_headers(self):
        # 添加认证头
        return {'Authorization': 'Bearer token'}
    
    def full_request_data(self, validated_request_data):
        # 添加通用参数
        validated_request_data['app_id'] = 'my_app'
        return validated_request_data

# 调用
result = ExternalAPI().request({'user_id': 123})
```

### 自动发现机制

drf_resource 会自动发现项目中的资源：

```python
# 项目结构示例
myproject/
├── resources.py          # resource.xxx 可访问
├── api/
│   ├── default.py        # api.xxx 可访问
│   └── resources.py      # api.xxx 可访问
└── adapter/
    ├── default.py        # adapter.xxx 可访问
    ├── community/
    │   └── resources.py  # 优先级高于 default.py
    └── enterprise/
        └── resources.py  # 优先级高于 default.py

# 使用示例
from drf_resource import resource, api, adapter

# 访问 resource
result = resource.plugin.install_plugin(...)

# 访问 api
result = api.bkdata.query_data(...)

# 访问 adapter（自动选择平台版本）
result = adapter.cc.get_business_list(...)
```

### ResourceViewSet 路由配置

#### 标准方法

```python
class UserViewSet(ResourceViewSet):
    resource_routes = [
        # GET /api/users/ (列表)
        ResourceRoute(method='GET', resource_class=UserListResource),
        
        # POST /api/users/ (创建)
        ResourceRoute(method='POST', resource_class=UserCreateResource),
        
        # GET /api/users/{id}/ (详情)
        ResourceRoute(
            method='GET',
            resource_class=UserDetailResource,
            pk_field='id'
        ),
        
        # PUT /api/users/{id}/ (更新)
        ResourceRoute(
            method='PUT',
            resource_class=UserUpdateResource,
            pk_field='id'
        ),
        
        # DELETE /api/users/{id}/ (删除)
        ResourceRoute(
            method='DELETE',
            resource_class=UserDeleteResource,
            pk_field='id'
        ),
    ]
```

#### 自定义端点

```python
class UserViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute(
            method='GET',
            resource_class=UserProfileResource,
            endpoint='profile',  # 自定义端点
            pk_field='id',      # 详情路由
        ),
        ResourceRoute(
            method='POST',
            resource_class=UserLoginResource,
            endpoint='login',   # 列表路由
        ),
    ]
```

对应的 URL：
- `GET /api/users/{id}/profile/`
- `POST /api/users/login/`

#### 分页支持

```python
ResourceRoute(
    method='GET',
    resource_class=UserListResource,
    enable_paginate=True,  # 启用分页
)
```

#### 装饰器支持

```python
from django.views.decorators.cache import cache_control

ResourceRoute(
    method='GET',
    resource_class=UserListResource,
    decorators=[cache_control(max_age=300)],  # 应用装饰器
)
```

### 异步任务支持

使用 Celery 执行异步任务：

```python
# 发起异步任务
result = UserResource().delay({'user_id': 123})
# 返回: {'task_id': 'xxx-xxx-xxx'}

# 高级用法
result = UserResource().apply_async(
    {'user_id': 123},
    countdown=60,  # 60 秒后执行
    expires=300,   # 300 秒后过期
)
```

### 批量请求

```python
resource = UserResource()

# 批量请求（并发执行）
results = resource.bulk_request([
    {'user_id': 1},
    {'user_id': 2},
    {'user_id': 3},
])

# 忽略异常
results = resource.bulk_request(
    [{'user_id': i} for i in range(1, 101)],
    ignore_exceptions=True
)
```

## 🔧 高级配置

### Django Settings 配置

```python
DRF_RESOURCE = {
    # ========== 自动发现配置 ==========
    'AUTO_DISCOVERY': True,  # 是否启用自动发现
    
    # ========== 资源数据收集 ==========
    'RESOURCE_DATA_COLLECT_ENABLED': False,  # 是否启用数据收集
    'RESOURCE_DATA_COLLECT_RATIO': 0.1,     # 采样比例
    
    # ========== 认证配置 ==========
    'USERNAME_FIELD': 'username',           # 用户名字段
    'DEFAULT_USERNAME': 'system',           # 默认用户名
    
    # ========== HTTP Resource 配置 ==========
    'HTTP_AUTH_ENABLED': False,             # 是否启用认证
    'HTTP_AUTH_HEADER': 'Authorization',    # 认证头
    'HTTP_AUTH_PARAMS': {},                 # 认证参数
    'HTTP_STANDARD_FORMAT': True,           # 是否标准响应格式
    'HTTP_TIMEOUT': 60,                     # 超时时间（秒）
    'HTTP_VERIFY_SSL': True,                # 是否验证 SSL
    
    # ========== Celery 配置 ==========
    'CELERY_QUEUE': 'celery_resource',      # Celery 队列名
    
    # ========== OpenTelemetry 配置 ==========
    'OPENTELEMETRY_ENABLED': False,         # 是否启用追踪
}
```

### 缓存配置

```python
from drf_resource.cache import CacheTypeItem

# 基础缓存
cache_type = CacheTypeItem(
    key="user_cache",     # 缓存名称
    timeout=60,           # 过期时间（秒）
    user_related=True,    # 是否用户相关
    label="用户数据缓存"   # 说明
)

# 带条件的缓存
cache_type = CacheTypeItem(
    key="backend_cache",
    timeout=300,
    user_related=False,
    label="后台缓存"
)

class MyResource(CacheResource):
    cache_type = cache_type
    backend_cache_type = CacheTypeItem(key="backend_cache", timeout=600)  # 后台用户缓存时间
    
    def cache_write_trigger(self, response):
        # 控制何时写入缓存
        return response.get('status') == 'success'
```

## 🎯 最佳实践

### 1. 资源拆分原则

将复杂的业务逻辑拆分为多个小的 Resource：

```python
# ✅ 好的做法
class UserDetailResource(Resource):
    """获取用户详情"""
    pass

class UserStatsResource(Resource):
    """获取用户统计"""
    pass

# ❌ 不好的做法
class UserAllInfoResource(Resource):
    """获取用户所有信息（包含太多逻辑）"""
    pass
```

### 2. 复用 Resource

在 ViewSet 中复用相同的 Resource：

```python
class UserViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute(method='GET', resource_class=UserDetailResource, pk_field='id'),
        ResourceRoute(method='GET', resource_class=UserDetailResource, endpoint='info', pk_field='id'),
    ]
```

### 3. 命名约定

遵循命名约定以启用自动发现：

```
Resource 类名:           XxxResource
请求序列化器:            XxxRequestSerializer
响应序列化器:            XxxResponseSerializer
```

### 4. 错误处理

使用框架提供的异常处理：

```python
from drf_resource.exceptions import CustomException

class UserResource(Resource):
    def perform_request(self, validated_request_data):
        user = User.objects.filter(id=validated_request_data['user_id']).first()
        if not user:
            raise CustomException('用户不存在')
        return user
```

## 📖 API Explorer

drf_resource 内置了 API Explorer，提供可视化的 API 调试界面。

### 启用 API Explorer

在 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'drf_resource.api_explorer',
]
```

在 `urls.py` 中添加：

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path('api-explorer/', include('drf_resource.api_explorer.urls')),
]
```

访问 `/api-explorer/` 即可使用 API Explorer。

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

- [腾讯蓝鲸监控平台](https://github.com/TencentBlueKing/bk-monitor)
- [httpflex - 强大的 HTTP 客户端库](https://github.com/HACK-WU/httpflex-py)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [蓝鲸社区](https://bk.tencent.com/s-mart/community)