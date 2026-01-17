# DRF Resource 通用化改造计划

## 项目背景

`drf_resource` 模块原位于 bkmonitor（蓝鲸监控）项目中，现已独立出来进行通用化改造，目的是使其成为一个通用的 Django REST Framework 资源化框架，能够在其他项目中快速使用。

## 改造目标

1. 移除所有蓝鲸特定依赖和硬编码
2. 将核心功能抽象为通用实现
3. 提供可选的高级功能支持（如 OpenTelemetry）
4. 完善项目文档和配置
5. 确保测试独立运行

## 改造计划

### 🔴 高优先级任务（核心功能清理）

#### 1. 清理蓝鲸特定依赖 - 重命名 errors/api.py 中的 BKAPIError 为通用 APIError

**问题：**
- `BKAPIError` 包含蓝鲸特定的错误消息模板和命名
- `DevopsNotDeployedError` 依赖蓝盾概念

**改造方案：**
- 将 `BKAPIError` 重命名为 `APIError`（或 `HTTPAPIError`）
- 移除错误消息中的蓝鲸相关描述
- 保留通用的 API 错误处理逻辑
- 保留错误码体系，但使其可配置

**影响文件：**
- `drf_resource/errors/api.py`
- `drf_resource/exceptions.py`（引用处）
- `drf_resource/contrib/api.py`（引用处）
- `drf_resource/contrib/nested_api.py`（引用处）

---

#### 2. 清理蓝鲸特定依赖 - 重构 contrib/api.py (APIResource) 为通用 HTTPResource

**问题：**
- `APIResource` 专为蓝鲸 APIGW/ESB 设计
- 包含 `bk_app_code`, `bk_app_secret`, `bk_username` 等蓝鲸特定参数
- 错误处理依赖蓝鲸权限中心（IAM）错误码
- 使用蓝鲸标准的 API 响应格式

**改造方案：**
- 将 `APIResource` 重命名为 `HTTPResource`（或保留为 `APIResource` 但通用化）
- 将认证参数（app_code, app_secret, username）改为可配置
- 将请求头（`x-bkapi-authorization`）改为可自定义
- 移除蓝鲸权限中心特定错误处理（9900403, 35999999）
- 移除蓝鲸 IAM 相关配置（`BK_IAM_SAAS_HOST`）
- 支持自定义 API 响应格式解析

**新增配置项：**
```python
# settings.py
DRF_RESOURCE_HTTP_AUTH_ENABLED = True  # 是否启用认证
DRF_RESOURCE_HTTP_AUTH_HEADER = 'Authorization'  # 认证头名称
DRF_RESOURCE_HTTP_AUTH_PARAMS = {  # 认证参数模板
    'app_code': '{APP_CODE}',
    'app_secret': '{APP_SECRET}',
    'username': '{USERNAME}',
}
DRF_RESOURCE_HTTP_STANDARD_FORMAT = True  # 是否使用标准格式 {result, code, message, data}
```

**影响文件：**
- `drf_resource/contrib/api.py`
- `drf_resource/errors/iam.py`（可能需要删除）
- `drf_resource/README.md`

---

#### 3. 清理蓝鲸特定依赖 - 删除或重构 contrib/nested_api.py

**问题：**
- `KernelAPIResource` 依赖 `kernel_api`, `query_api` 等蓝鲸模块
- 依赖 `monitor_v3.yaml` 配置文件
- 使用 `settings.ROLE == "api"` 判断
- 处理蓝鲸监控特有的循环调用场景
**改造方案（选项A - 删除）：**
- 直接删除 `contrib/nested_api.py`，因为这是蓝鲸监控特定功能

**改造方案（选项B - 通用化）：**
- 将 `KernelAPIResource` 改为 `DirectAPIResource`（直连 API Resource）
- 移除 YAML 配置依赖，改为 URL 映射配置
- 移除对 `kernel_api`, `query_api` 的导入
- 提供通用的内部 API 调用能力

**建议：** 采用选项A，删除此文件，因为功能过于特定

**影响文件：**
- `drf_resource/contrib/nested_api.py`（删除）
- `drf_resource/__init__.py`（移除导出）
- `drf_resource/README.md`

---

#### 4. 清理蓝鲸特定依赖 - 更新 utils/auth.py 为通用认证工具

**问题：**
- `get_bk_login_ticket()` 函数名为蓝鲸特定
- 仅支持蓝鲸登录票据（bk_ticket, bk_token）

**改造方案：**
- 将 `get_bk_login_ticket()` 重命名为 `get_auth_token()` 或保持不变但通用化
- 支持通用的 token 获取方式
- 支持自定义 token 获取逻辑

**影响文件：**
- `drf_resource/utils/auth.py`
- `drf_resource/contrib/api.py`（引用处）

---

### 🟡 中优先级任务（配置与可选性）

#### 5. 配置项通用化 - 创建 settings.py 定义配置项

**问题：**
- 代码中大量使用 `getattr(settings, 'XXX')`
- 没有统一的配置文档
- 蓝鲸特定配置散落各处

**改造方案：**
- 创建或完善 `drf_resource/settings.py`，定义默认配置
- 在文档中列出所有可配置项
- 移除蓝鲸特定配置的硬编码

**配置项清单：**
```python
# 核心配置
DRF_RESOURCE_AUTO_DISCOVERY = True  # 是否自动发现 Resource
DRF_RESOURCE_RESOURCE_DATA_COLLECT_ENABLED = False  # 是否收集 Resource 请求数据
DRF_RESOURCE_RESOURCE_DATA_COLLECT_RATIO = 0.1  # 采样比例

# 认证配置
DRF_RESOURCE_USERNAME_FIELD = 'username'  # 用户名字段
DRF_RESOURCE_DEFAULT_USERNAME = 'system'  # 默认用户名

# HTTP Resource 配置
DRF_RESOURCE_HTTP_TIMEOUT = 60  # 默认超时时间
DRF_RESOURCE_HTTP_VERIFY_SSL = True  # 是否验证 SSL

# Celery 配置（必选功能）
DRF_RESOURCE_CELERY_QUEUE = 'celery_resource'  # Celery 队列名称

# 可选功能配置
DRF_RESOURCE_OPENTELEMETRY_ENABLED = False  # 是否启用 OpenTelemetry
```

**影响文件：**
- `drf_resource/settings.py`（新建或完善）
- `drf_resource/base.py`
- `drf_resource/models.py`
- `drf_resource/contrib/api.py`
- `drf_resource/tasks.py`
- `drf_resource/cache.py`
- `drf_resource/README.md`

---

#### 6. 可选依赖处理 - OpenTelemetry 改为可选依赖

**问题：**
- `base.py` 中直接导入 `opentelemetry`
- `tasks.py`、`thread_backend.py` 中使用 opentelemetry
- 没有降级方案

**改造方案：**
- 在所有使用 opentelemetry 的地方添加 try-except
- 提供 no-op 降级实现
- 在 `requirements.txt` 中标记为可选依赖

**示例代码：**
```python
try:
    from opentelemetry import trace
    from opentelemetry.trace.status import Status, StatusCode

    tracer = trace.get_tracer(__name__)
except ImportError:
    # 降级实现
    class _NoOpTracer:
        def start_as_current_span(self, *args, **kwargs):
            return self

        class Span:
            def __enter__(self): return self
            def __exit__(self, *args, **kwargs): pass
            def set_status(self, *args, **kwargs): pass
            def add_event(self, *args, **kwargs): pass

        def start_as_current_span(self, *args, **kwargs):
            return self.Span()

    tracer = _NoOpTracer()
```

**影响文件：**
- `drf_resource/base.py`
- `drf_resource/exceptions.py`
- `drf_resource/utils/thread_backend.py`
- `requirements.txt`

---

#### 7. 保留 Celery 任务支持（必选依赖）

**说明：**
- Celery 异步任务是 drf_resource 的核心功能之一
- 保持 Celery 为必选依赖，不进行降级处理
- 确保异步任务功能完整可用

**需要确认：**
- `tasks.py` 中的 Celery 配置是否需要通用化
- `base.py` 中的 `delay()`, `apply_async()` 方法是否需要调整
- Celery 队列名称配置是否可自定义

**影响文件：**
- `drf_resource/tasks.py`
- `drf_resource/base.py`
- `requirements.txt`

---

#### 8. 更新版权和文档 - 修改所有文件头部版权声明

**问题：**
- 所有 Python 文件头部都是蓝鲸监控的版权声明
- 包含 "蓝鲸智云 - 监控平台" 等特定信息

**改造方案：**
- 更新版权声明为通用 MIT 协议
- 移除蓝鲸特定信息
- 可选择添加原贡献者信息

**新版权模板：**
```python
# -*- coding: utf-8 -*-
"""
DRF Resource - Django REST Framework 资源化框架
Copyright (C) 2024-2025

Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
```

**影响文件：**
- 所有 `.py` 文件（约 30+ 文件）

---

#### 9. 更新版权和文档 - 更新 README.md 为通用项目文档

**问题：**
- README.md 仍然包含 "从蓝鲸 bk_resource 剥离" 等描述
- 提及 "不建议生产环境使用"
- 缺少完整的使用文档

**改造方案：**
- 重写 README.md，强调通用性
- 添加完整的安装、配置、使用文档
- 添加 API 文档链接
- 更新示例代码，移除蓝鲸特定内容

**新 README 结构：**
```markdown
# DRF Resource

Django REST Framework 资源化框架，提供声明式 API 开发体验。

## 特性

- 🚀 声明式 API 开发：基于 Resource 定义业务逻辑
- 🔄 自动序列化：自动匹配 Request/Response Serializer
- 📦 可选缓存：内置 Redis 缓存支持
- 🔌 HTTP 客户端：内置 HTTP Resource 请求外部 API
- 📊 可观测性：可选 OpenTelemetry 支持
- ⚙️ 异步任务：内置 Celery 支持
- 🔍 自动发现：自动扫描和注册 Resource

## 安装

```bash
pip install drf-resource
```

## 快速开始

...

## 配置

...

## 文档

...

## 示例

...
```

**影响文件：**
- `README.md`
- `drf_resource/README.md`

---

#### 10. 代码重构 - 搜索并移除所有 bkmonitor/bk_ 蓝鲸相关硬编码

**问题：**
- 代码中可能存在其他蓝鲸相关的硬编码
- 日志消息中包含 "蓝鲸" 等字样
- 错误消息包含蓝鲸特定术语

**改造方案：**
- 使用 grep 搜索所有 `bk_`, `蓝鲸`, `bkmonitor`, `blueking` 等关键词
- 逐个审查并通用化
- 确保日志和错误消息使用通用术语

**搜索命令：**
```bash
grep -r "bk_\|蓝鲸\|bkmonitor\|blueking" drf_resource --include="*.py"
```

**影响文件：**
- 多个文件（需根据搜索结果确定）

---

### 🟢 低优先级任务（发布准备）

#### 11. 测试和打包 - 创建 requirements.txt 和 setup.py/pyproject.toml

**问题：**
- 没有 `requirements.txt`（只有 bkmonitor 项目中的）
- 没有 `setup.py` 或 `pyproject.toml` 用于 pip 安装
- pyproject.toml 中配置指向 bkmonitor

**改造方案：**
- 创建 `requirements.txt`，列出核心依赖和可选依赖
- 创建或完善 `pyproject.toml`，包含包信息
- 配置打包和发布流程

**requirements.txt 结构：**
```
# 核心依赖
Django>=3.2
djangorestframework>=3.12
six>=1.15
celery>=5.0  # Celery 异步任务支持（必选）
requests>=2.25  # HTTP 客户端支持（必选）

# 可选依赖
# Redis 缓存
redis>=4.0

# OpenTelemetry
opentelemetry-api>=1.0
opentelemetry-sdk>=1.0

# 开发依赖
pytest>=7.0
pytest-django>=4.0
pytest-cov>=3.0
black>=22.0
```

**pyproject.toml 结构：**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "drf-resource"
version = "0.1.0"
description = "Django REST Framework 资源化框架"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "DRF Resource Contributors"}
]
keywords = ["django", "rest", "framework", "resource", "api"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Framework :: Django",
    "Framework :: Django :: 3.2",
    "Framework :: Django :: 4.0",
    "Framework :: Django :: 4.1",
    "Framework :: Django :: 4.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "Django>=3.2",
    "djangorestframework>=3.12",
    "six>=1.15",
    "celery>=5.0",  # Celery 异步任务支持（必选）
    "requests>=2.25",  # HTTP 客户端支持（必选）
]

[project.optional-dependencies]
cache = ["redis>=4.0"]
otel = ["opentelemetry-api>=1.0", "opentelemetry-sdk>=1.0"]
dev = ["pytest>=7.0", "pytest-django>=4.0", "pytest-cov>=3.0", "black>=22.0"]
all = ["drf-resource[cache,otel]"]

[project.urls]
Homepage = "https://github.com/your-org/drf-resource"
Documentation = "https://drf-resource.readthedocs.io"
Repository = "https://github.com/your-org/drf-resource.git"

[tool.setuptools.packages.find]
include = ["drf_resource*"]

[tool.setuptools.package-data]
drf_resource = ["**/*.py"]
```

**影响文件：**
- `requirements.txt`（新建）
- `pyproject.toml`（修改）

---

#### 12. 测试和打包 - 修复测试脚本, 确保测试独立运行

**问题：**
- `run_tests.sh` 脚本硬编码了 bkmonitor 虚拟环境路径
- 测试依赖 bkmonitor 的某些配置
- 测试不够独立

**改造方案：**
- 修改测试脚本，使用当前 Python 环境
- 确保测试有独立的 Django 配置
- 移除对 bkmonitor 的依赖

**新测试脚本：**
```bash
#!/bin/bash

# 使用系统 Python 或虚拟环境 Python
PYTHON=${PYTHON:-python}

# 设置环境变量
export DJANGO_SETTINGS_MODULE=drf_resource.tests.settings
export PYTHONPATH=.

# 运行测试
$PYTHON -m pytest tests/ -v "$@"
```

**影响文件：**
- `run_tests.sh`
- `tests/conftest.py`
- `tests/__init__.py`

---

## 改造顺序建议

1. **第一阶段**（高优先级 1-4）：核心功能清理，确保代码通用化
2. **第二阶段**（中优先级 5-7）：配置和可选依赖处理
3. **第三阶段**（中优先级 8-10）：文档和代码清理
4. **第四阶段**（低优先级 11-12）：测试和打包准备

## 注意事项

1. **向后兼容性**：如果已有人在项目中使用，考虑提供兼容层或迁移指南
2. **测试覆盖**：每个改动都需要有对应的测试用例
3. **文档同步**：代码改动时同步更新文档
4. **版本控制**：每次完成一个阶段后打 tag，便于回滚
5. **社区反馈**：如果已有使用者，提前沟通改造计划

## 完成标准

- [ ] 所有蓝鲸特定依赖已移除
- [ ] 所有代码可以通过 `pip install drf-resource` 安装使用
- [ ] 测试可以独立运行，不依赖 bkmonitor
- [ ] OpenTelemetry 为可选依赖，Celery 保持为必选依赖
- [ ] README.md 包含完整的安装和使用文档
- [ ] 所有文件头部版权已更新
- [ ] 代码中无蓝鲸相关硬编码

## 附录

### 依赖清单

#### 核心依赖（必选）
- Django >= 3.2
- djangorestframework >= 3.12
- six >= 1.15
- celery >= 5.0（异步任务）
- requests >= 2.25（HTTP 客户端）

#### 可选依赖
- redis >= 4.0（缓存功能）
- opentelemetry-api, opentelemetry-sdk >= 1.0（可观测性）
- drf-yasg >= 1.20（API 文档）

### 文件清单

需要修改的文件数量：约 30+ 个

主要目录：
- `drf_resource/` - 核心代码
- `drf_resource/contrib/` - 扩展功能
- `drf_resource/errors/` - 错误定义
- `drf_resource/utils/` - 工具函数
- `tests/` - 测试代码

---

*最后更新：2025-01-18*
