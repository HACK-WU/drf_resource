# DRF Resource 配置参考

## 概述

本文档列出 `drf_resource/settings.py` 中 `DEFAULT` 定义的**全部 17 个配置项**，涵盖缓存、认证、HTTP 客户端、Celery 及 API 文档等维度的配置。所有配置均通过 Django 的 `DRF_RESOURCE` 字典传入。

---

## 配置方式

在项目的 `settings.py` 中定义 `DRF_RESOURCE` 字典：

```python
DRF_RESOURCE = {
    "HTTP_TIMEOUT": 30,
    "HTTP_VERIFY_SSL": False,
    "ENABLE_API_DOCS": True,
}
```

未提供的键将使用**默认值**。框架通过 `DrfResourceSettings` 读取该字典，支持向后兼容的降级机制（`drf_resource/settings.py:52`）。

---

## 配置项总览

| 分类 | 配置项 | 类型 | 默认值 |
|------|--------|------|--------|
| 缓存 | `DEFAULT_USING_CACHE` | `str` (可导入路径) | `"drf_resource.cache.DefaultUsingCache"` |
| 数据收集 | `RESOURCE_DATA_COLLECT_ENABLED` | `bool` | `False` |
| 数据收集 | `RESOURCE_DATA_COLLECT_RATIO` | `float` | `0.1` |
| 认证 | `USERNAME_FIELD` | `str` | `"username"` |
| 认证 | `DEFAULT_USERNAME` | `str` | `"system"` |
| HTTP 客户端 | `HTTP_AUTH_ENABLED` | `bool` | `False` |
| HTTP 客户端 | `HTTP_AUTH_HEADER` | `str` | `"Authorization"` |
| HTTP 客户端 | `HTTP_AUTH_PARAMS` | `dict` | `{}` |
| HTTP 客户端 | `HTTP_STANDARD_FORMAT` | `bool` | `True` |
| HTTP 客户端 | `HTTP_TIMEOUT` | `int` (秒) | `60` |
| HTTP 客户端 | `HTTP_VERIFY_SSL` | `bool` | `True` |
| Celery | `CELERY_QUEUE` | `str` | `"celery_resource"` |
| API 文档 | `ENABLE_API_DOCS` | `bool` | `True` |
| API 文档 | `SCHEMA_CACHE_TIMEOUT` | `int` (秒) | `3600` |
| API 文档 | `DOCS_TAG_THRESHOLD` | `int` | `100` |
| API 文档 | `DOCS_PATH_PREFIX_GROUPING_ENABLED` | `bool` | `True` |
| API 文档 | `DOCS_PATH_PREFIX_THRESHOLD` | `int` | `50` |

---

## 缓存配置

### `DEFAULT_USING_CACHE`

- **类型**：`str`（可导入的缓存类路径）
- **默认值**：`"drf_resource.cache.DefaultUsingCache"`
- **说明**：指定 Resource 框架默认使用的缓存后端。必须为可导入的类路径，会在运行时被动态加载。若需接入 Redis 或自定义缓存逻辑，可继承 `DefaultUsingCache` 并替换此配置。
- **使用位置**：`drf_resource/settings.py:7`, `drf_resource/settings.py:33`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "DEFAULT_USING_CACHE": "myapp.cache.RedisUsingCache",
  }
  ```

---

## 数据收集配置

### `RESOURCE_DATA_COLLECT_ENABLED`

- **类型**：`bool`
- **默认值**：`False`
- **说明**：是否启用 Resource 请求采样记录。开启后，框架会自动将 Resource 的入参和出参写入 `resource_data` 表，便于线上问题排查。首次访问必定记录，后续按 `RESOURCE_DATA_COLLECT_RATIO` 采样。
- **使用位置**：`drf_resource/settings.py:8`, `drf_resource/settings.py:34`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "RESOURCE_DATA_COLLECT_ENABLED": True,
  }
  ```

### `RESOURCE_DATA_COLLECT_RATIO`

- **类型**：`float`
- **默认值**：`0.1`
- **说明**：Resource 请求采样比例。`0.1` 表示首次记录后，后续 10% 的请求会被采样写入 `resource_data` 表。仅在 `RESOURCE_DATA_COLLECT_ENABLED=True` 时生效。若某个 Resource 设置了 `support_data_collect = False`，则跳过该 Resource。
- **使用位置**：`drf_resource/settings.py:9`

---

## 认证配置

### `USERNAME_FIELD`

- **类型**：`str`
- **默认值**：`"username"`
- **说明**：定义获取当前请求用户名时使用的字段名。框架通过 `get_request_username()` 获取用户名时使用此字段。若 Django User 模型使用其他字段（如 `email`）作为主标识，可修改此配置。
- **使用位置**：`drf_resource/settings.py:11`, `drf_resource/settings.py:36`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "USERNAME_FIELD": "email",
  }
  ```

### `DEFAULT_USERNAME`

- **类型**：`str`
- **默认值**：`"system"`
- **说明**：当无法在请求上下文中获取用户名时（如 Celery 任务、命令行脚本），使用的默认用户名回退值。用于异步任务、定时任务等无 HTTP request 的场景。
- **使用位置**：`drf_resource/settings.py:12`, `drf_resource/settings.py:37`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "DEFAULT_USERNAME": "cron_job",
  }
  ```

---

## HTTP 客户端配置（APIResource）

以下配置专用于 `APIResource` 及其子类（基于 `httpflex` 的 HTTP 客户端能力）。

### `HTTP_AUTH_ENABLED`

- **类型**：`bool`
- **默认值**：`False`
- **说明**：是否在 `APIResource` 请求中启用自动认证。开启后，框架会自动在 HTTP 请求头或查询参数中注入认证信息。
- **使用位置**：`drf_resource/settings.py:14`, `drf_resource/settings.py:39`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "HTTP_AUTH_ENABLED": True,
  }
  ```

### `HTTP_AUTH_HEADER`

- **类型**：`str`
- **默认值**：`"Authorization"`
- **说明**：启用认证时，使用的 HTTP Header 名称。若后端使用自定义认证头（如 `X-API-Key`），可修改此配置。
- **使用位置**：`drf_resource/settings.py:15`, `drf_resource/settings.py:40`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "HTTP_AUTH_HEADER": "X-BK-Token",
  }
  ```

### `HTTP_AUTH_PARAMS`

- **类型**：`dict`
- **默认值**：`{}`
- **说明**：启用认证时，附加到 HTTP 请求中的静态认证参数字典。通常用于传递 `bk_app_code`、`bk_app_secret` 等固定凭证。`APIResource` 会自动将此字典注入到请求中。
- **使用位置**：`drf_resource/settings.py:16`, `drf_resource/settings.py:41`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "HTTP_AUTH_PARAMS": {
          "bk_app_code": "my_app",
          "bk_app_secret": "secret_key",
      },
  }
  ```

### `HTTP_STANDARD_FORMAT`

- **类型**：`bool`
- **默认值**：`True`
- **说明**：控制 `APIResource` 的响应数据解析行为。`True` 时，从标准 `{ "result": true, "data": {...} }` 格式中提取 `data` 字段；`False` 时直接返回原始响应体。适用于对接非标准格式的第三方 API。
- **使用位置**：`drf_resource/settings.py:17`, `drf_resource/settings.py:42`, `drf_resource/resources/api.py:78`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "HTTP_STANDARD_FORMAT": False,  # 适用于返回裸数据的 API
  }
  ```

### `HTTP_TIMEOUT`

- **类型**：`int`（秒）
- **默认值**：`60`
- **说明**：`APIResource` 的默认 HTTP 请求超时时间。超过此时间未收到响应将抛出超时异常。根据网络环境和后端服务性能调整。
- **使用位置**：`drf_resource/settings.py:18`, `drf_resource/settings.py:43`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "HTTP_TIMEOUT": 30,
  }
  ```

### `HTTP_VERIFY_SSL`

- **类型**：`bool`
- **默认值**：`True`
- **说明**：是否验证 HTTPS 请求的 SSL 证书。**开发环境**可设为 `False` 以跳过自签名证书校验；**生产环境强烈建议保持 `True`**。
- **使用位置**：`drf_resource/settings.py:19`, `drf_resource/settings.py:44`
- **示例**：
  ```python
  # 仅用于开发/测试环境
  DRF_RESOURCE = {
      "HTTP_VERIFY_SSL": False,
  }
  ```

---

## Celery 配置

### `CELERY_QUEUE`

- **类型**：`str`
- **默认值**：`"celery_resource"`
- **说明**：`Resource.delay()` 和 `Resource.apply_async()` 执行异步任务时使用的默认 Celery 队列名。若需与其他业务队列隔离，可指定独立队列。
- **使用位置**：`drf_resource/settings.py:21`, `drf_resource/settings.py:46`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "CELERY_QUEUE": "high_priority",
  }
  ```

---

## API 文档配置（drf-spectacular）

> 这些配置控制基于 `drf-spectacular` 自动生成的 OpenAPI 文档行为。

### `ENABLE_API_DOCS`

- **类型**：`bool`
- **默认值**：`True`
- **说明**：是否启用 API 文档生成。设为 `False` 将禁用文档装饰器（Schema decorator），减少运行开销，且不会在 `/docs/` 注册文档路由。适用于无需文档的生产环境或纯内部服务。
- **使用位置**：`drf_resource/settings.py:23`, `drf_resource/settings.py:48`, `drf_resource/views/viewsets.py:52`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "ENABLE_API_DOCS": False,
  }
  ```

### `SCHEMA_CACHE_TIMEOUT`

- **类型**：`int`（秒）
- **默认值**：`3600`（1 小时）
- **说明**：OpenAPI Schema 的缓存超时时间。Schema 生成涉及全量遍历 ViewSet 和 Serializer，计算开销较大。缓存可显著提升 `/schema/` 接口性能。设为 `0` 完全禁用缓存。
- **使用位置**：`drf_resource/settings.py:24`, `drf_resource/contrib/spectacular.py:501-508`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "SCHEMA_CACHE_TIMEOUT": 0,       # 开发时禁用缓存
      # 或
      "SCHEMA_CACHE_TIMEOUT": 7200,    # 生产环境缓存 2 小时
  }
  ```

### `DOCS_TAG_THRESHOLD`

- **类型**：`int`
- **默认值**：`100`
- **说明**：单个标签（业务模块）下的 API 数量警告阈值。超过此数量时，文档界面会显示警告提示，提醒开发者该模块 API 过多，建议拆分为更细粒度的模块。
- **使用位置**：`drf_resource/settings.py:25`, `drf_resource/contrib/spectacular.py:515`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "DOCS_TAG_THRESHOLD": 50,
  }
  ```

### `DOCS_PATH_PREFIX_GROUPING_ENABLED`

- **类型**：`bool`
- **默认值**：`True`
- **说明**：是否启用路径前缀二级分组功能。设为 `True` 后，框架会尝试按 URL 路径前缀对 API 进行二次分组（如 `/api/v1/users/` 和 `/api/v1/orders/` 归为不同组），以改善大型项目的文档可读性。仅在 `ENABLE_API_DOCS=True` 时生效。
- **使用位置**：`drf_resource/settings.py:26`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "DOCS_PATH_PREFIX_GROUPING_ENABLED": False,  # 禁用二级分组
  }
  ```

### `DOCS_PATH_PREFIX_THRESHOLD`

- **类型**：`int`
- **默认值**：`50`
- **说明**：启用路径前缀二级分组的 API 数量阈值。仅当项目总 API 数量超过此值时，`DOCS_PATH_PREFIX_GROUPING_ENABLED` 才会实际生效。避免小型项目因过度分组导致文档冗余。
- **使用位置**：`drf_resource/settings.py:27`
- **示例**：
  ```python
  DRF_RESOURCE = {
      "DOCS_PATH_PREFIX_THRESHOLD": 30,
  }
  ```

---

## 完整配置示例

```python
# settings.py

DRF_RESOURCE = {
    # === 缓存 ===
    "DEFAULT_USING_CACHE": "drf_resource.cache.DefaultUsingCache",

    # === 数据收集（调试用）===
    "RESOURCE_DATA_COLLECT_ENABLED": False,
    "RESOURCE_DATA_COLLECT_RATIO": 0.1,

    # === 认证 ===
    "USERNAME_FIELD": "username",
    "DEFAULT_USERNAME": "system",

    # === HTTP 客户端 ===
    "HTTP_AUTH_ENABLED": False,
    "HTTP_AUTH_HEADER": "Authorization",
    "HTTP_AUTH_PARAMS": {},
    "HTTP_STANDARD_FORMAT": True,
    "HTTP_TIMEOUT": 60,
    "HTTP_VERIFY_SSL": True,

    # === Celery ===
    "CELERY_QUEUE": "celery_resource",

    # === API 文档 ===
    "ENABLE_API_DOCS": True,
    "SCHEMA_CACHE_TIMEOUT": 3600,
    "DOCS_TAG_THRESHOLD": 100,
    "DOCS_PATH_PREFIX_GROUPING_ENABLED": True,
    "DOCS_PATH_PREFIX_THRESHOLD": 50,
}
```

---

## 相关文档

- [README](../README.md) — 项目概述与快速开始
- [Resource 框架自动发现与使用](Resource框架自动发现与使用.md) — 自动发现机制、扫描规则、全局入口使用
- [Resource 框架使用小技巧](Resource框架使用小技巧.md) — 线程安全、批量请求、异步任务、调试技巧
