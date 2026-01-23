# API Explorer 模块

## 概述

API Explorer 是 drf_resource 框架的开发者工具，用于查看和调试项目中的 API 资源。

## 功能特性

- **API 发现**：自动扫描并展示项目中所有 `APIResource` 子类
- **接口文档**：展示请求/响应参数结构
- **在线调试**：支持在线调用第三方 API
- **环境隔离**：仅在开发/测试环境启用
- **参数脱敏**：自动脱敏敏感参数

## 快速开始

### 1. 配置

在项目的 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'drf_resource.api_explorer',
]

# 可选配置
DRF_RESOURCE = {
    # 是否启用 API Explorer（None: 自动检测，True: 强制启用，False: 强制禁用）
    'API_EXPLORER_ENABLED': None,
    
    # URL 前缀
    'API_EXPLORER_URL_PREFIX': 'api-explorer',
    
    # 是否启用在线调用
    'API_EXPLORER_ENABLE_INVOKE': True,
    
    # 是否记录审计日志
    'API_EXPLORER_ENABLE_AUDIT': False,
}
```

### 2. 路由配置

在项目的 `urls.py` 中添加：

```python
from django.urls import path, include

urlpatterns = [
    # ... 其他路由
    path('api-explorer/', include('drf_resource.urls')),
]
```

### 3. 访问

启动项目后，访问：

- **主页**：`http://your-domain/api-explorer/`
- **API 目录**：`http://your-domain/api-explorer/catalog/`
- **API 详情**：`http://your-domain/api-explorer/api_detail/?module=xxx&api_name=yyy`
- **在线调用**：`POST http://your-domain/api-explorer/invoke/`

## API 端点说明

### 1. 主页（IndexView）

**路径**：`GET /api-explorer/`

**功能**：返回 API Explorer 主页信息

**响应示例**：
```json
{
    "result": true,
    "message": "API Explorer 主页面",
    "data": {
        "title": "API Explorer",
        "description": "用于查看和调试项目中的 API 资源",
        "endpoints": {
            "catalog": "/api-explorer/catalog/",
            "api_detail": "/api-explorer/api_detail/",
            "invoke": "/api-explorer/invoke/"
        }
    }
}
```

### 2. API 目录（CatalogView）

**路径**：`GET /api-explorer/catalog/`

**功能**：获取所有 API 的目录列表

**请求参数**：
- `search`（可选）：搜索关键词
- `module`（可选）：过滤指定模块

**响应示例**：
```json
{
    "result": true,
    "data": {
        "modules": [
            {
                "name": "bkdata",
                "display_name": "计算平台",
                "apis": [
                    {
                        "name": "query_data",
                        "class_name": "QueryDataResource",
                        "module": "bkdata",
                        "label": "查询数据",
                        "method": "POST",
                        "base_url": "http://...",
                        "action": "/v3/dataquery/query/",
                        "full_url": "http://.../v3/dataquery/query/",
                        "has_request_serializer": true,
                        "has_response_serializer": false
                    }
                ]
            }
        ],
        "total": 156
    },
    "message": "success"
}
```

### 3. API 详情（APIDetailView）

**路径**：`GET /api-explorer/api_detail/`

**功能**：获取单个 API 的详细信息

**请求参数**：
- `module`（必填）：模块名
- `api_name`（必填）：接口名

**响应示例**：
```json
{
    "result": true,
    "data": {
        "module": "bkdata",
        "api_name": "query_data",
        "class_name": "QueryDataResource",
        "label": "查询数据",
        "method": "POST",
        "full_url": "http://.../v3/dataquery/query/",
        "doc": "查询计算平台数据",
        "request_params": [
            {
                "name": "sql",
                "type": "string",
                "required": true,
                "description": "查询 SQL",
                "default": null
            }
        ],
        "response_params": [...]
    },
    "message": "success"
}
```

### 4. 在线调用（InvokeView）

**路径**：`POST /api-explorer/invoke/`

**功能**：在线调用指定的外部 API

**请求参数**：
```json
{
    "module": "bkdata",
    "api_name": "query_data",
    "params": {
        "sql": "SELECT * FROM table LIMIT 10"
    }
}
```

**响应示例（成功）**：
```json
{
    "result": true,
    "data": {
        "success": true,
        "response": {...},
        "duration": 1.23,
        "request_params": {...},
        "timestamp": "2026-01-12T10:30:00Z"
    },
    "message": "调用成功"
}
```

**响应示例（失败）**：
```json
{
    "result": false,
    "data": {
        "success": false,
        "error_message": "权限不足",
        "error_code": "9900403",
        "duration": 0.5,
        "request_params": {...},
        "timestamp": "2026-01-12T10:30:00Z"
    },
    "message": "调用失败"
}
```

## 环境检测

API Explorer 会自动检测运行环境，仅在以下情况下启用：

1. **显式配置**：`settings.DRF_RESOURCE['API_EXPLORER_ENABLED'] = True`
2. **DEBUG 模式**：`settings.DEBUG = True`
3. **环境变量**：`ENV` 设置为 `dev`、`test`、`development`、`testing`、`local`

非测试环境访问时会返回 403 Forbidden。

## 安全特性

### 参数脱敏

敏感参数会自动脱敏，包括：
- `bk_app_secret`
- `password`
- `token`
- 其他包含 `secret`、`passwd`、`key` 的字段

脱敏方式：保留前后各 4 位字符，中间替换为 `***`

### 审计日志

每次 API 调用都会记录日志，包括：
- 调用用户
- 模块名和接口名
- 请求参数（脱敏）
- 调用结果
- 耗时

## 架构设计

### 模块结构

```
api_explorer/
├── __init__.py          # 应用初始化
├── apps.py              # Django AppConfig
├── exceptions.py        # 自定义异常
├── permissions.py       # 环境检测权限类
├── services.py          # 核心服务层（发现/调用）
├── views.py             # 视图层
└── urls.py              # 路由配置
```

### 核心组件

#### 1. APIDiscoveryService

负责扫描并提取 API 资源的元数据：
- 遍历 `api.*` 命名空间
- 提取 `APIResource` 子类的元数据
- 调用 `generate_doc()` 生成请求/响应结构

#### 2. APIInvokeService

负责动态调用第三方 API：
- 动态获取 Resource 实例
- 调用 `resource.request(params)`
- 异常捕获和格式化
- 参数脱敏

#### 3. IsTestEnvironment

权限类，用于环境检测：
- 多重判断机制（配置 > DEBUG > 环境变量）
- 非测试环境返回 403

## 开发指南

### 添加新功能

1. 在 `services.py` 中添加服务逻辑
2. 在 `views.py` 中添加视图
3. 在 `urls.py` 中注册路由
4. 更新文档

### 测试

```bash
# 运行单元测试
pytest drf_resource/api_explorer/tests/

# 检查代码质量
flake8 drf_resource/api_explorer/
```

## 常见问题

### Q1: 如何在生产环境禁用？

在 `settings.py` 中配置：
```python
DRF_RESOURCE = {
    'API_EXPLORER_ENABLED': False,
}
```

### Q2: 如何自定义 URL 前缀？

在 `urls.py` 中修改路由：

```python
path('custom-prefix/', include('drf_resource.urls')),
```

### Q3: 如何查看审计日志？

审计日志会自动记录到 Django 日志系统，可以在日志文件中查看。

## 后续计划

- [ ] 前端页面开发（HTML/JS/CSS）
- [ ] 静态资源集成
- [ ] 参数模板保存
- [ ] 历史调用记录
- [ ] 收藏常用 API

## 技术栈

- Django REST Framework
- drf_resource 框架
- Python 3.8+

## 许可证

MIT License
