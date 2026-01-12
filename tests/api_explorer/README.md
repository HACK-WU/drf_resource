# API Explorer 测试套件

本目录包含 `drf_resource.api_explorer` 模块的完整单元测试。

## 测试结构

```
tests/
├── __init__.py
├── conftest.py              # pytest fixtures 和测试配置
├── test_exceptions.py       # 异常类测试
├── test_permissions.py      # 权限检查测试
├── test_services.py         # 服务层测试
└── test_views.py            # 视图层测试
```

## 运行测试

### 运行所有测试
```bash
pytest drf_resource/api_explorer/tests/
```

### 运行特定测试文件
```bash
pytest drf_resource/api_explorer/tests/test_services.py
```

### 运行特定测试类
```bash
pytest drf_resource/api_explorer/tests/test_services.py::TestAPIDiscoveryService
```

### 运行特定测试方法
```bash
pytest drf_resource/api_explorer/tests/test_services.py::TestAPIDiscoveryService::test_discover_all_apis_success
```

### 显示详细输出
```bash
pytest -v drf_resource/api_explorer/tests/
```

### 显示打印输出
```bash
pytest -s drf_resource/api_explorer/tests/
```

### 生成覆盖率报告
```bash
pytest --cov=drf_resource.api_explorer --cov-report=html drf_resource/api_explorer/tests/
```

## 测试覆盖

### test_exceptions.py
- ✅ APIExplorerException 基类测试
- ✅ ResourceNotFoundError 测试
- ✅ InvocationError 测试
- ✅ EnvironmentDeniedError 测试

### test_permissions.py
- ✅ is_test_environment() 函数测试
  - 显式配置优先级
  - DEBUG 模式检测
  - 环境变量检测
  - 优先级顺序测试
- ✅ IsTestEnvironment 权限类测试
  - has_permission() 测试
  - has_object_permission() 测试

### test_services.py
- ✅ APIDiscoveryService 测试
  - discover_all_apis() - 发现所有 API
  - 搜索和过滤功能
  - 元数据提取
  - URL 拼接
  - get_api_detail() - 获取 API 详情
- ✅ APIInvokeService 测试
  - invoke_api() - 调用 API
  - 参数脱敏
  - 错误处理
  - 持续时间和时间戳记录

### test_views.py
- ✅ IndexView 测试
  - GET 请求
  - 权限检查
- ✅ CatalogView 测试
  - GET 请求（带/不带参数）
  - 搜索和过滤
  - 参数校验
  - 错误处理
- ✅ APIDetailView 测试
  - GET 请求
  - 必填参数校验
  - 资源未找到处理
  - 错误处理
- ✅ InvokeView 测试
  - POST 请求
  - 参数校验
  - 用户名提取
  - 调用成功/失败处理
  - 错误处理

## Fixtures 说明

### conftest.py 提供的 Fixtures

- `api_client`: REST Framework 测试客户端
- `mock_resource_class`: Mock Resource 类
- `mock_fail_resource_class`: Mock 失败的 Resource 类
- `mock_api_module`: Mock API 模块
- `mock_settings_api_explorer_enabled`: Mock API Explorer 启用配置
- `mock_settings_api_explorer_disabled`: Mock API Explorer 禁用配置
- `mock_debug_mode`: Mock DEBUG=True
- `mock_production_mode`: Mock 生产环境
- `mock_env_dev`: Mock ENV=dev
- `mock_env_production`: Mock ENV=production

## 注意事项

1. **环境隔离**: 所有测试使用 fixtures 进行环境隔离，不会影响实际配置
2. **Mock 使用**: 大量使用 `unittest.mock` 和 `monkeypatch` 进行依赖隔离
3. **权限测试**: 测试覆盖了不同环境下的权限检查
4. **错误处理**: 测试覆盖了各种异常情况和边界条件

## 测试最佳实践

1. **每个测试独立**: 每个测试方法应该独立运行，不依赖其他测试
2. **使用 fixtures**: 充分利用 pytest fixtures 进行测试准备
3. **清晰的命名**: 测试方法名清晰描述测试内容
4. **完整的断言**: 每个测试应包含充分的断言
5. **边界条件**: 测试应覆盖正常情况、异常情况和边界条件
