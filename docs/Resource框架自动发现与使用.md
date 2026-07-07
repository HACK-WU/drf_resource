# Resource 框架自动发现与使用

## 概述

drf_resource 框架提供了强大的自动发现机制，能够自动扫描项目中的资源模块并注册到全局入口，使代码逻辑实现基于 Resource 原子的组装和复用。

## 自动发现入口

自动发现功能的核心入口位于 `drf_resource/management/root.py` 中的 ResourceManager。

## ResourceManager 扫描机制

ResourceManager 会自动扫描各模块的以下目录：

| 目录类型 | 扫描规则 | 示例 |
|----------|----------|------|
| resource | `resource.模块名` → `模块/resources.py` | `resource.cc` → `cc/resources.py` |
| adapter | `adapter.模块名` → `模块/adapter/default.py` | `adapter.cc` → `cc/adapter/default.py` |
| api | `api.模块名` → `模块/api/default.py` | `api.bkdata` → `bkdata/api/default.py` |

### adapter 变体覆盖

adapter 模块支持平台差异化覆盖：

```
模块/adapter/
├── default.py              # 默认实现
├── community/
│   └── resources.py        # 社区版覆盖（优先级高于 default）
└── enterprise/
    └── resources.py        # 企业版覆盖（优先级高于 default）
```

当存在 `模块/adapter/${platform}/resources.py` 时，会覆盖 `default.py` 中的同名 Resource。

## 全局导入

```python
# 基类
from drf_resource import Resource

# 扩展类
from drf_resource import APIResource, CacheResource, FaultTolerantResource

# 自动发现管理器
from drf_resource import adapter, api, resource
```

## 两种使用方式

### 方式一：通过全局入口调用（推荐）

```python
from drf_resource import resource

# 线程安全，自动完成请求/响应序列化
result = resource.alert.search_alert({"id": "xxx", "limit": 10})
```

**优势**：
- 天然线程安全
- 自动完成请求/响应序列化
- 无需显式导入具体 Resource 类

### 方式二：显式导入调用

```python
from api.tapd import SomeResource

# 显式导入并实例化
result = SomeResource().request(params)
```

## TLS 参数透传

HTTP 请求自动携带以下认证参数（由 APIResource 基类注入）：

- `bk_app_code`：应用编码
- `bk_app_secret`：应用密钥
- `bk_username`：用户名

## 关键特性

### 1. bulk_request() - 并行批量请求

```python
results = resource.issue.issue_top_n_result.bulk_request([
    {"start_time": t0, "end_time": t1, "bk_biz_id": 2},
    {"start_time": t1, "end_time": t2, "bk_biz_id": 2},
])
```

### 2. delay() / apply_async() - 异步任务

```python
# 简单异步
task_info = resource.alert.some_resource.delay({"id": "xxx"})
# 返回: {"task_id": "celery-task-id-xxx"}

# 高级异步（传 Celery 参数）
task_info = resource.alert.some_resource.apply_async(
    {"id": "xxx"},
    countdown=60,   # 延迟60秒执行
    queue="high",   # 指定队列
)
```

### 3. ThreadPool 自动继承上下文

ThreadPool 会自动把主线程的以下上下文同步到工作线程：

- local 对象中的所有数据（Django request/session/thread-local 变量）
- timezone（当前时区）
- language（当前语言）
- trace_context（OpenTelemetry trace 上下文）

这意味着在 Resource 里可以直接 `get_request_username()`、`get_request_tenant_id()`，即使在 `bulk_request` 的子线程中也能正确拿到值。

### 4. 全局入口命名映射

```
resource.alert.search_alert
│      │         │
│      │         └── snake_case（从 SearchAlertResource 去掉 Resource 后转下划线）
│      └── 模块路径名（fta_web/alert/ → alert）
└── 全局入口 ResourceManager
```

- `resource` → 各模块 `resources.py`
- `api` → `api/xxx/default.py`（封装远程 ESB/APIGW）
- `adapter` → `xxx/adapter/default.py`（按平台差异覆盖）

## 内部调用复用

在实际项目中，Resource 之间可以互相调用：

```python
# kernel_api/resource/alert.py
class ListAlertResource(Resource):
    def perform_request(self, validated_request_data):
        # 内部调用其他模块的 resource
        return resource.alert.search_alert(validated_request_data)
```

前端不直接调用 `kernel_api/resource/` 中的 Resource，而是通过 `kernel_api/views/` 中的 ResourceViewSet 暴露。

## 依赖关系

```
Resource
├── views.ResourceViewSet (HTTP 暴露)
├── models.ResourceDataManager (请求采样记录)
├── management.root.ResourceShortcut (懒加载代理)
│   └── management.finder.ResourceFinder (自动发现)
└── utils.thread_backend.ThreadPool (多线程并发)
```
