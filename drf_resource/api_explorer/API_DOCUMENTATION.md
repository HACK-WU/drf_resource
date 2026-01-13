# API Explorer - API 文档

## 概述

API Explorer 提供了一套 RESTful API 接口，用于查看和调试项目中的 API 资源。所有接口均需要在测试/开发环境下访问。

**基础 URL**：`http://your-domain/`

**环境要求**：
- 测试环境（`DEBUG=True` 或 `ENV in ['dev', 'test', 'development', 'testing', 'local']`）
- 非测试环境访问会返回 `403 Forbidden`

---

## 通用响应格式

### 成功响应

```json
{
    "result": true,
    "data": {...},
    "message": "success"
}
```

### 失败响应

```json
{
    "result": false,
    "data": null,
    "message": "错误描述"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足（非测试环境） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## API 端点列表

### 1. 主页信息

获取 API Explorer 的主页信息和可用端点。

**接口地址**：`GET /api_index/`

**请求参数**：无

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| result | boolean | 请求是否成功 |
| data | object | 返回数据 |
| data.title | string | 标题 |
| data.description | string | 描述 |
| data.endpoints | object | 端点完整URL映射（包含域名） |
| data.endpoints_info | array | 端点详细信息列表 |
| data.endpoints_info[].name | string | 端点名称 |
| data.endpoints_info[].url | string | 端点完整URL（包含域名） |
| data.endpoints_info[].method | string | HTTP 方法 |
| data.endpoints_info[].description | string | 端点描述 |
| data.endpoints_info[].params | array | 参数列表 |
| message | string | 响应消息 |

**注意**：返回的URL是完整的绝对URL，包含协议、域名和路径，会根据当前请求的域名动态生成。

**响应示例**：

```json
{
    "result": true,
    "message": "API Explorer 主页面",
    "data": {
        "title": "API Explorer",
        "description": "用于查看和调试项目中的 API 资源",
        "endpoints": {
            "catalog": "http://localhost:8000/catalog/",
            "api_detail": "http://localhost:8000/api_detail/",
            "invoke": "http://localhost:8000/invoke/",
            "modules": "http://localhost:8000/api_modules/"
        },
        "endpoints_info": [
            {
                "name": "catalog",
                "url": "http://localhost:8000/catalog/",
                "method": "GET",
                "description": "获取 API 目录列表，支持搜索和模块过滤",
                "params": [
                    {
                        "name": "search",
                        "type": "string",
                        "required": false,
                        "description": "搜索关键词，匹配模块名、接口名、类名、标签",
                        "default": null
                    },
                    {
                        "name": "module",
                        "type": "string",
                        "required": false,
                        "description": "过滤指定模块",
                        "default": null
                    }
                ]
            },
            {
                "name": "api_detail",
                "url": "http://localhost:8000/api_detail/",
                "method": "GET",
                "description": "获取单个 API 的详细信息，包括请求/响应参数结构",
                "params": [
                    {
                        "name": "module",
                        "type": "string",
                        "required": true,
                        "description": "模块名",
                        "default": null
                    },
                    {
                        "name": "api_name",
                        "type": "string",
                        "required": true,
                        "description": "API 名称",
                        "default": null
                    }
                ]
            },
            {
                "name": "invoke",
                "url": "http://localhost:8000/invoke/",
                "method": "POST",
                "description": "在线调用指定的第三方 API，并返回调用结果",
                "params": [
                    {
                        "name": "module",
                        "type": "string",
                        "required": true,
                        "description": "模块名",
                        "default": null
                    },
                    {
                        "name": "api_name",
                        "type": "string",
                        "required": true,
                        "description": "API 名称",
                        "default": null
                    },
                    {
                        "name": "params",
                        "type": "object",
                        "required": false,
                        "description": "请求参数（JSON 对象）",
                        "default": {}
                    }
                ]
            },
            {
                "name": "modules",
                "url": "http://localhost:8000/api_modules/",
                "method": "GET",
                "description": "获取所有可用的模块列表，支持模糊查询",
                "params": [
                    {
                        "name": "search",
                        "type": "string",
                        "required": false,
                        "description": "搜索关键词，匹配模块名或展示名称",
                        "default": null
                    }
                ]
            }
        ]
    }
}
```

**cURL 示例**：

```bash
curl -X GET "http://localhost:8000/api_index/"
```

---

### 2. 获取所有模块

获取项目中所有可用的模块列表，支持模糊搜索。

**接口地址**：`GET /api_modules/`

**请求参数**（Query Parameters）：

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| search | string | 否 | 搜索关键词，匹配模块名或展示名称 | `data` |

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| result | boolean | 请求是否成功 |
| data | object | 返回数据 |
| data.modules | array | 模块列表 |
| data.modules[].name | string | 模块名称 |
| data.modules[].display_name | string | 模块展示名称 |
| data.modules[].api_count | integer | 该模块下的 API 数量 |
| data.total | integer | 模块总数 |
| message | string | 响应消息 |

**响应示例**：

```json
{
    "result": true,
    "data": {
        "modules": [
            {
                "name": "bkdata",
                "display_name": "计算平台",
                "api_count": 23
            },
            {
                "name": "cmdb",
                "display_name": "配置平台",
                "api_count": 45
            },
            {
                "name": "job",
                "display_name": "作业平台",
                "api_count": 12
            }
        ],
        "total": 3
    },
    "message": "success"
}
```

**cURL 示例**：

```bash
# 获取所有模块
curl -X GET "http://localhost:8000/api_modules/"

# 搜索包含 "data" 的模块
curl -X GET "http://localhost:8000/api_modules/?search=data"
```

**错误响应**：

```json
{
    "result": false,
    "message": "参数校验失败",
    "errors": {
        "search": ["确保这个字段不为空。"]
    }
}
```

---

### 3. 获取 API 目录

获取项目中所有 API 资源的目录列表，支持搜索和模块过滤。

**接口地址**：`GET /catalog/`

**请求参数**（Query Parameters）：

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| search | string | 否 | 搜索关键词，匹配模块名、接口名、类名、标签 | `query` |
| module | string | 否 | 过滤指定模块 | `bkdata` |

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| result | boolean | 请求是否成功 |
| data | object | 返回数据 |
| data.modules | array | 模块列表 |
| data.modules[].name | string | 模块名称 |
| data.modules[].display_name | string | 模块展示名称 |
| data.modules[].apis | array | 该模块下的 API 列表 |
| data.modules[].apis[].name | string | API 名称（下划线格式） |
| data.modules[].apis[].class_name | string | Resource 类名 |
| data.modules[].apis[].module | string | 所属模块 |
| data.modules[].apis[].label | string | API 描述标签 |
| data.modules[].apis[].method | string | HTTP 方法（GET/POST/PUT/DELETE） |
| data.modules[].apis[].base_url | string | 基础 URL |
| data.modules[].apis[].action | string | 接口路径 |
| data.modules[].apis[].full_url | string | 完整 URL |
| data.modules[].apis[].has_request_serializer | boolean | 是否有请求序列化器 |
| data.modules[].apis[].has_response_serializer | boolean | 是否有响应序列化器 |
| data.total | integer | API 总数 |
| message | string | 响应消息 |

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
                        "base_url": "http://paas.example.com/api/c/compapi/v2/bkdata/",
                        "action": "/v3/dataquery/query/",
                        "full_url": "http://paas.example.com/api/c/compapi/v2/bkdata/v3/dataquery/query/",
                        "has_request_serializer": true,
                        "has_response_serializer": false
                    },
                    {
                        "name": "create_data_source",
                        "class_name": "CreateDataSourceResource",
                        "module": "bkdata",
                        "label": "创建数据源",
                        "method": "POST",
                        "base_url": "http://paas.example.com/api/c/compapi/v2/bkdata/",
                        "action": "/v3/databus/data_sources/",
                        "full_url": "http://paas.example.com/api/c/compapi/v2/bkdata/v3/databus/data_sources/",
                        "has_request_serializer": true,
                        "has_response_serializer": true
                    }
                ]
            },
            {
                "name": "cmdb",
                "display_name": "配置平台",
                "apis": [
                    {
                        "name": "search_business",
                        "class_name": "SearchBusinessResource",
                        "module": "cmdb",
                        "label": "查询业务",
                        "method": "POST",
                        "base_url": "http://paas.example.com/api/c/compapi/v2/cc/",
                        "action": "/search_business/",
                        "full_url": "http://paas.example.com/api/c/compapi/v2/cc/search_business/",
                        "has_request_serializer": true,
                        "has_response_serializer": true
                    }
                ]
            }
        ],
        "total": 156
    },
    "message": "success"
}
```

**cURL 示例**：

```bash
# 获取所有 API
curl -X GET "http://localhost:8000/catalog/"

# 搜索包含 "query" 关键词的 API
curl -X GET "http://localhost:8000/catalog/?search=query"

# 获取指定模块的 API
curl -X GET "http://localhost:8000/catalog/?module=bkdata"

# 组合使用
curl -X GET "http://localhost:8000/catalog/?module=bkdata&search=data"
```

**错误响应**：

```json
{
    "result": false,
    "message": "参数校验失败",
    "errors": {
        "search": ["确保这个字段不为空。"]
    }
}
```

---

### 4. 获取 API 详细信息

获取单个 API 的详细信息，包括请求/响应参数结构。

**接口地址**：`GET /api_detail/`

**请求参数**（Query Parameters）：

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| module | string | 是 | 模块名 | `bkdata` |
| api_name | string | 是 | API 名称 | `query_data` |

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| result | boolean | 请求是否成功 |
| data | object | API 详细信息 |
| data.module | string | 模块名 |
| data.api_name | string | API 名称 |
| data.class_name | string | Resource 类名 |
| data.label | string | API 描述 |
| data.method | string | HTTP 方法 |
| data.full_url | string | 完整 URL |
| data.doc | string | 接口文档说明 |
| data.request_params | array | 请求参数列表 |
| data.request_params[].name | string | 参数名 |
| data.request_params[].type | string | 参数类型 |
| data.request_params[].required | boolean | 是否必填 |
| data.request_params[].description | string | 参数描述 |
| data.request_params[].default | any | 默认值 |
| data.response_params | array | 响应参数列表 |
| data.response_params[].name | string | 字段名 |
| data.response_params[].type | string | 字段类型 |
| data.response_params[].description | string | 字段描述 |
| message | string | 响应消息 |

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
        "full_url": "http://paas.example.com/api/c/compapi/v2/bkdata/v3/dataquery/query/",
        "doc": "查询计算平台数据接口",
        "request_params": [
            {
                "name": "sql",
                "type": "string",
                "required": true,
                "description": "查询 SQL 语句",
                "default": null
            },
            {
                "name": "prefer_storage",
                "type": "string",
                "required": false,
                "description": "优先存储类型",
                "default": ""
            },
            {
                "name": "bk_username",
                "type": "string",
                "required": false,
                "description": "用户名",
                "default": null
            }
        ],
        "response_params": [
            {
                "name": "list",
                "type": "array",
                "description": "查询结果列表"
            },
            {
                "name": "total",
                "type": "integer",
                "description": "总记录数"
            }
        ]
    },
    "message": "success"
}
```

**cURL 示例**：

```bash
curl -X GET "http://localhost:8000/api_detail/?module=bkdata&api_name=query_data"
```

**错误响应**：

1. 参数缺失：

```json
{
    "result": false,
    "message": "参数校验失败",
    "errors": {
        "module": ["该字段是必填项。"],
        "api_name": ["该字段是必填项。"]
    }
}
```

2. API 不存在：

```json
{
    "result": false,
    "message": "API 不存在: bkdata.invalid_api",
    "data": null
}
```

---

### 5. 在线调用 API

在线调用指定的第三方 API，并返回调用结果。

**接口地址**：`POST /invoke/`

**Content-Type**：`application/json`

**请求参数**（Request Body）：

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| module | string | 是 | 模块名 | `bkdata` |
| api_name | string | 是 | API 名称 | `query_data` |
| params | object | 否 | 请求参数（JSON 对象） | `{"sql": "SELECT * FROM table"}` |

**请求示例**：

```json
{
    "module": "bkdata",
    "api_name": "query_data",
    "params": {
        "sql": "SELECT * FROM table LIMIT 10",
        "prefer_storage": "es"
    }
}
```

**响应参数**：

| 字段 | 类型 | 说明 |
|------|------|------|
| result | boolean | 请求是否成功 |
| data | object | 调用结果数据 |
| data.success | boolean | API 调用是否成功 |
| data.response | any | 成功时的响应数据 |
| data.error_message | string | 失败时的错误信息 |
| data.error_code | string | 失败时的错误码 |
| data.duration | float | 调用耗时（秒） |
| data.request_params | object | 实际发送的请求参数（敏感信息已脱敏） |
| data.timestamp | string | 调用时间（ISO 8601 格式） |
| message | string | 响应消息 |

**响应示例（成功）**：

```json
{
    "result": true,
    "data": {
        "success": true,
        "response": {
            "list": [
                {
                    "id": 1,
                    "name": "测试数据",
                    "value": 100
                }
            ],
            "total": 1
        },
        "error_message": null,
        "error_code": null,
        "duration": 1.234,
        "request_params": {
            "sql": "SELECT * FROM table LIMIT 10",
            "prefer_storage": "es",
            "bk_username": "admin",
            "bk_app_secret": "test***cret"
        },
        "timestamp": "2026-01-12T10:30:00.123456Z"
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
        "response": null,
        "error_message": "权限不足：用户无权访问该资源",
        "error_code": "9900403",
        "duration": 0.456,
        "request_params": {
            "sql": "SELECT * FROM table LIMIT 10",
            "bk_username": "test_user",
            "bk_app_secret": "test***cret"
        },
        "timestamp": "2026-01-12T10:30:00.123456Z"
    },
    "message": "调用失败"
}
```

**cURL 示例**：

```bash
curl -X POST "http://localhost:8000/invoke/" \
  -H "Content-Type: application/json" \
  -d '{
    "module": "bkdata",
    "api_name": "query_data",
    "params": {
      "sql": "SELECT * FROM table LIMIT 10",
      "prefer_storage": "es"
    }
  }'
```

**错误响应**：

1. 参数校验失败：

```json
{
    "result": false,
    "message": "参数校验失败",
    "errors": {
        "module": ["该字段是必填项。"],
        "api_name": ["该字段是必填项。"]
    }
}
```

2. API 不存在：

```json
{
    "result": false,
    "message": "API 不存在: bkdata.invalid_api",
    "data": null
}
```

3. API 调用异常：

```json
{
    "result": false,
    "message": "API 调用异常: Connection timeout",
    "data": null
}
```

---

## 安全特性

### 1. 环境隔离

API Explorer 仅在以下环境中可用：

- `DEBUG = True`
- `ENV in ['dev', 'test', 'development', 'testing', 'local']`
- 或显式配置 `DRF_RESOURCE['API_EXPLORER_ENABLED'] = True`

非测试环境访问将返回：

```json
{
    "detail": "您没有执行该操作的权限。"
}
```

HTTP 状态码：`403 Forbidden`

### 2. 参数脱敏

调用 API 时，以下敏感参数会自动脱敏：

- `bk_app_secret`
- `password`
- `token`
- 包含 `secret`、`passwd`、`key` 的字段

**脱敏规则**：
- 长度 > 8：保留前后各 4 位，中间替换为 `***`
- 长度 ≤ 8：全部替换为 `***`

**示例**：

| 原始值 | 脱敏后 |
|--------|--------|
| `test_secret_key_12345678` | `test***5678` |
| `short` | `***` |

### 3. 审计日志

所有 API 调用都会记录审计日志，包括：

- 调用用户
- 模块名和接口名
- 请求参数（脱敏后）
- 调用结果（成功/失败）
- 错误码
- 调用耗时
- 时间戳

日志级别：`INFO`（成功）、`ERROR`（失败）

---

## 错误码说明

| 错误码 | 说明 | 示例 |
|--------|------|------|
| 404 | 资源不存在 | `API 不存在: bkdata.query_data` |
| 403 | 权限不足 | `API Explorer 仅在开发/测试环境可用` |
| 400 | 参数错误 | `参数校验失败：module 字段是必填项` |
| 500 | 服务器错误 | `获取 API 目录失败: Internal Server Error` |
| 9900403 | 第三方 API 权限不足 | 来自第三方 API 的错误码 |

---

## 使用场景

### 场景 1：浏览所有 API

```bash
# 1. 获取 API 目录
curl -X GET "http://localhost:8000/catalog/"

# 2. 搜索特定 API
curl -X GET "http://localhost:8000/catalog/?search=query"

# 3. 查看某个模块的所有 API
curl -X GET "http://localhost:8000/catalog/?module=bkdata"
```

### 场景 2：查看 API 详情

```bash
# 获取 API 的详细文档
curl -X GET "http://localhost:8000/api_detail/?module=bkdata&api_name=query_data"
```

### 场景 3：调试 API

```bash
# 1. 查看 API 详情，了解参数结构
curl -X GET "http://localhost:8000/api_detail/?module=bkdata&api_name=query_data"

# 2. 调用 API 进行测试
curl -X POST "http://localhost:8000/invoke/" \
  -H "Content-Type: application/json" \
  -d '{
    "module": "bkdata",
    "api_name": "query_data",
    "params": {
      "sql": "SELECT * FROM table LIMIT 10"
    }
  }'
```

### 场景 4：集成到前端

```javascript
// 获取 API 目录
fetch('/catalog/')
  .then(response => response.json())
  .then(data => {
    console.log('API 总数:', data.data.total);
    console.log('模块列表:', data.data.modules);
  });

// 调用 API
fetch('/invoke/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    module: 'bkdata',
    api_name: 'query_data',
    params: {
      sql: 'SELECT * FROM table LIMIT 10'
    }
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.result) {
      console.log('调用成功:', data.data.response);
    } else {
      console.error('调用失败:', data.data.error_message);
    }
  });
```

---

## 配置选项

在项目的 `settings.py` 中配置：

```python
DRF_RESOURCE = {
    # 是否启用 API Explorer
    # None: 自动检测（默认）
    # True: 强制启用
    # False: 强制禁用
    'API_EXPLORER_ENABLED': None,
    
    # URL 前缀（默认为空，直接使用路径）
    'API_EXPLORER_URL_PREFIX': '',
    
    # 是否启用在线调用功能
    'API_EXPLORER_ENABLE_INVOKE': True,
    
    # 是否记录审计日志
    'API_EXPLORER_ENABLE_AUDIT': True,
}
```

---

## 性能考虑

### 响应时间

| 端点 | 平均响应时间 | 说明 |
|------|--------------|------|
| `/catalog/` | 50-200ms | 取决于 API 数量 |
| `/api_detail/` | 10-50ms | 单个 API 元数据提取 |
| `/invoke/` | 变化较大 | 取决于第三方 API 响应时间 |

### 优化建议

1. **API 目录缓存**：对于 `/catalog/` 端点，可以考虑添加缓存
2. **分页加载**：如果 API 数量过多，建议添加分页参数
3. **超时控制**：调用第三方 API 时设置合理的超时时间

---

## 常见问题

### Q1: 为什么访问返回 403？

**原因**：当前环境不是测试环境。

**解决**：
1. 检查 `settings.DEBUG` 是否为 `True`
2. 检查环境变量 `ENV` 是否为测试环境值
3. 或在 `settings.py` 中显式配置：
   ```python
   DRF_RESOURCE = {'API_EXPLORER_ENABLED': True}
   ```

### Q2: 如何查看所有可用的 API？

使用 `/catalog/` 端点即可获取所有 API 列表。

### Q3: 调用 API 失败怎么办？

1. 检查 `data.error_message` 字段获取错误详情
2. 查看 `data.error_code` 判断错误类型
3. 检查请求参数是否正确
4. 查看日志文件获取更多信息

### Q4: 敏感参数会被记录吗？

不会。所有敏感参数在记录日志前都会自动脱敏。

---

## 更新日志

### v1.0.0 (2026-01-12)

- ✅ 实现 API 目录查询
- ✅ 实现 API 详情查询
- ✅ 实现在线调用功能
- ✅ 实现环境检测与权限控制
- ✅ 实现参数脱敏保护
- ✅ 实现审计日志记录

---

## 技术支持

如有问题，请联系开发团队或提交 Issue。

**项目地址**：`/data/workspace/drf_resource/drf_resource/api_explorer/`

**相关文档**：
- [README.md](./README.md) - 使用指南
- [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md) - 实现报告