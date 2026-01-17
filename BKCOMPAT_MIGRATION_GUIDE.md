# DRF Resource 改造影响分析文档

**文档版本**: v0.1.0  
**创建日期**: 2025-01-12  
**目的**: 记录 drf_resource 通用化改造对 bkmonitor 项目的影响，提供适配指南

---

## 目录

1. [概述](#概述)
2. [改造范围](#改造范围)
3. [API 变更影响](#api-变更影响)
4. [配置变更影响](#配置变更影响)
5. [行为变更影响](#行为变更影响)
6. [破坏性变更](#破坏性变更)
7. [向后兼容方案](#向后兼容方案)
8. [迁移步骤](#迁移步骤)
9. [测试验证](#测试验证)
10. [常见问题](#常见问题)

---

## 概述

drf_resource 模块正在进行通用化改造，目标是将其从 bkmonitor（蓝鲸监控）项目中剥离出来，成为一个通用的 Django REST Framework 资源化框架。

**改造目标**:
- 移除所有蓝鲸特定的依赖和硬编码
- 支持通过配置进行灵活定制
- 使 drf_resource 可以独立在其他项目中使用
- 保持 bkmonitor 项目的向后兼容性

**适用对象**: bkmonitor 项目及其依赖 drf_resource 的其他项目

---

## 改造范围

### 核心改造内容

#### 1. 移除蓝鲸特定依赖
- `BKAPIError` → `APIError`（或保留兼容别名）
- 删除 `contrib/nested_api.py`
- 移除 `errors/iam.py` 中的蓝鲸 IAM 特定错误码
- 清理所有 `bk_` 前缀的硬编码

#### 2. 配置化改造
- `settings.APP_CODE` → `resource_settings.APP_CODE`
- `settings.ROLE` → `resource_settings.ROLE`
- `settings.BK_IAM_SAAS_HOST` → `resource_settings.BK_IAM_SAAS_HOST`
- `settings.BASE_DIR` → `resource_settings.BASE_DIR`

#### 3. 可选依赖处理
- OpenTelemetry 改为可选依赖，提供 no-op 降级实现
- Celery 保持为必选依赖

#### 4. 版权和文档
- 更新所有文件版权声明为通用 MIT 协议
- 移除 "蓝鲸智云 - 监控平台" 等特定描述

---

## API 变更影响

### 1. APIResource 类变更 ⚠️ **高影响**

#### 变更内容

`APIResource` 类的认证机制从硬编码改为配置化：

**改造前**（bkmonitor 当前使用）:
```python
# contrib/api.py
class APIResource(CacheResource):
    def get_headers(self):
        # 硬编码从 settings 读取
        headers["x-bkapi-authorization"] = f"{settings.APP_CODE}:{settings.SECRET_KEY}"
        headers["blueking-language"] = translation.get_language()
```

**改造后**（通用版本）:
```python
# contrib/api.py
class APIResource(CacheResource):
    def get_headers(self):
        # 从 resource_settings 读取配置
        headers = {}
        
        # 认证头（可配置）
        if resource_settings.HTTP_AUTH_ENABLED:
            headers[resource_settings.HTTP_AUTH_HEADER] = self._get_auth_token()
        
        # 语言头
        language = translation.get_language()
        if language:
            headers["Accept-Language"] = language  # 或自定义配置
        
        # 蓝鲸特定字段（兼容模式）
        if resource_settings.BK_API_MODE:
            headers["blueking-language"] = language
            headers["x-bkapi-authorization"] = self._get_bkapi_token()
        
        return headers
    
    def _get_auth_token(self):
        """获取认证令牌"""
        # 支持多种认证方式
        pass
    
    def _get_bkapi_token(self):
        """获取蓝鲸 API 认证令牌（兼容）"""
        app_code = resource_settings.APP_CODE or settings.APP_CODE
        app_secret = resource_settings.APP_SECRET or settings.SECRET_KEY
        return f"{app_code}:{app_secret}"
```

**新增配置项**:
```python
# settings.py
DRF_RESOURCE = {
    # 认证配置
    "APP_CODE": "bk_monitor",           # 应用编码
    "APP_SECRET": "your_app_secret",      # 应用密钥
    "BK_API_MODE": True,                  # 是否使用蓝鲸 API 模式（兼容）
    
    # HTTP 认证配置（通用）
    "HTTP_AUTH_ENABLED": False,           # 是否启用 HTTP 认证
    "HTTP_AUTH_HEADER": "Authorization",    # 认证头名称
    "HTTP_AUTH_PARAMS": {},                # 认证参数
    "HTTP_STANDARD_FORMAT": True,          # 是否使用标准格式
}
```

#### bkmonitor 影响

**影响程度**: ⚠️ **高影响**

**需要适配的内容**:

1. **配置适配**（必选）:
   ```python
   # bkmonitor/settings.py
   DRF_RESOURCE = {
       # 蓝鲸特定配置（保持兼容）
       "APP_CODE": settings.APP_CODE,
       "APP_SECRET": settings.SECRET_KEY,
       "BK_API_MODE": True,  # 启用蓝鲸 API 模式
       "BK_IAM_SAAS_HOST": settings.BK_IAM_SAAS_HOST,
       
       # 通用配置
       "HTTP_AUTH_ENABLED": False,  # 不启用通用 HTTP 认证
       "ROLE": settings.ROLE,
   }
   ```

2. **代码影响**（有限）:
   - 大部分使用 `APIResource` 的代码无需修改
   - 仅需确保 `DRF_RESOURCE` 配置正确

3. **行为影响**（低）:
   - 认证头生成逻辑可能略有变化（通过配置项保持兼容）
   - 错误消息中的 "蓝鲸" 术语可能改为 "系统"

#### 向后兼容方案

**方案 A - 在 bkmonitor 中配置 DRF_RESOURCE**（推荐）:
```python
# bkmonitor/settings.py
# 添加以下配置，保持向后兼容
DRF_RESOURCE = {
    # 蓝鲸特定配置
    "APP_CODE": getattr(settings, 'APP_CODE'),
    "APP_SECRET": getattr(settings, 'SECRET_KEY'),
    "BK_API_MODE": True,
    "BK_IAM_SAAS_HOST": getattr(settings, 'BK_IAM_SAAS_HOST'),
    
    # 保持 bkmonitor 的行为
    "HTTP_AUTH_ENABLED": False,
    "ROLE": getattr(settings, 'ROLE'),
}
```

**方案 B - 暂时迁移到本地版本**（不推荐）:
- 将 `contrib/api.py` 复制到 bkmonitor 项目中
- 使用 `bkmonitor.contrib.api` 覆盖 `drf_resource.contrib.api`

---

### 2. BKAPIError 类变更 ⚠️ **中影响**

#### 变更内容

**改造前**:
```python
# errors/api.py
class BKAPIError(Error):
    """蓝鲸 API 错误"""
    code = 3301001
```

**改造后**（选项 A - 重命名）:
```python
# errors/api.py
class APIError(Error):  # 重命名为通用名称
    """API 请求错误"""
    code = 3301001
```

**改造后**（选项 B - 保留兼容别名）:
```python
# errors/api.py
class APIError(Error):
    """API 请求错误"""
    code = 3301001

# 向后兼容别名（推荐）
BKAPIError = APIError
```

#### bkmonitor 影响

**影响程度**: ⚠️ **中影响**

**需要适配的内容**:

1. **导入更新**:
   ```python
   # 改造前
   from drf_resource.errors.api import BKAPIError
   
   # 改造后（选项 A - 需要修改）
   from drf_resource.errors.api import APIError
   
   # 改造后（选项 B - 无需修改）
   from drf_resource.errors.api import BKAPIError  # 仍可用
   ```

2. **错误实例化**:
   ```python
   # 如果使用选项 A，需要更新
   raise APIError(...)  # 而非 BKAPIError(...)
   
   # 如果使用选项 B，无需修改
   raise BKAPIError(...)  # 仍可用
   ```

#### 向后兼容方案

**推荐**: 使用选项 B（保留 `BKAPIError` 作为 `APIError` 的别名）

这样 bkmonitor 项目中的代码无需任何修改即可继续使用：

```python
# drf_resource/errors/api.py
class APIError(Error):
    """API 请求错误"""
    code = 3301001

# 向后兼容别名
BKAPIError = APIError
```

**搜索范围**: 需要搜索 bkmonitor 项目中所有使用 `BKAPIError` 的地方
```bash
# 搜索命令
grep -r "BKAPIError" bkmonitor --include="*.py"
```

---

### 3. nested_api.py 删除 ✅ **无影响**

#### 变更内容

**删除文件**: `drf_resource/contrib/nested_api.py`

**删除内容**:
- `KernelAPIResource` 类
- `load_api_yaml()` 函数
- 所有对 `kernel_api`, `query_api` 模块的引用

#### bkmonitor 影响

**影响程度**: ✅ **无影响**

**说明**:
- `nested_api.py` 从未在 `drf_resource/__init__.py` 中导出
- bkmonitor 项目应该没有直接使用 `KernelAPIResource`
- 如果 bkmonitor 确实使用了，需要重新实现类似逻辑

**验证方法**:
```bash
# 检查 bkmonitor 是否使用了 nested_api
grep -r "KernelAPIResource\|nested_api" bkmonitor --include="*.py"
```

---

### 4. 错误类变更 ⚠️ **低影响**

#### 变更内容

**删除或重命名**: `errors/iam.py` 中的蓝鲸 IAM 特定错误类

**变更前**:
```python
# errors/iam.py
class PermissionDeniedError(Error):
    """权限被拒绝"""
    code = 9900403

class APIPermissionDeniedError(PermissionDeniedError):
    """API 调用权限被拒绝"""
    code = 9900403  # 蓝鲸 IAM 特定错误码
```

**改造后**:
```python
# errors/iam.py
class PermissionDeniedError(Error):
    """权限被拒绝"""
    code = 403  # 使用通用 HTTP 状态码

# 向后兼容（可选）
class APIPermissionDeniedError(PermissionDeniedError):
    """权限被拒绝（蓝鲸兼容）"""
    code = 9900403
```

#### bkmonitor 影响

**影响程度**: ⚠️ **低影响**

**需要适配的内容**:
- 如果 bkmonitor 直接使用 `APIPermissionDeniedError`，可能需要更新错误码处理
- 如果 bkmonitor 有自定义的权限错误处理逻辑，需要验证是否受影响

**验证方法**:
```bash
# 检查 IAM 错误的使用
grep -r "APIPermissionDeniedError\|9900403" bkmonitor --include="*.py"
```

---

## 配置变更影响

### 1. 新增 DRF_RESOURCE 配置 ⚠️ **高影响**

#### 变更内容

改造后，drf_resource 统一通过 `settings.DRF_RESOURCE` 字典读取配置，而不是直接使用 `settings.xxx`。

#### bkmonitor 影响

**影响程度**: ⚠️ **高影响**

**必须适配**（在 bkmonitor/settings.py 中添加）:
```python
# bkmonitor/settings.py
# 新增 DRF_RESOURCE 配置字典
DRF_RESOURCE = {
    # ===== 必需配置 =====
    
    # 蓝鲸应用信息
    "APP_CODE": getattr(settings, 'APP_CODE'),
    "APP_SECRET": getattr(settings, 'SECRET_KEY'),
    
    # 蓝鲸特定配置
    "BK_API_MODE": True,
    "BK_IAM_SAAS_HOST": getattr(settings, 'BK_IAM_SAAS_HOST', ''),
    "ROLE": getattr(settings, 'ROLE', 'web'),
    
    # ===== 可选配置 =====
    
    # HTTP 配置
    "HTTP_AUTH_ENABLED": False,
    "HTTP_AUTH_HEADER": "Authorization",
    "HTTP_AUTH_PARAMS": {},
    "HTTP_STANDARD_FORMAT": True,
    
    # OpenTelemetry
    "OPENTELEMETRY_ENABLED": True,  # 如果 bkmonitor 使用了 OpenTelemetry
    
    # 资源收集
    "RESOURCE_DATA_COLLECT_ENABLED": getattr(settings, 'ENABLE_RESOURCE_DATA_COLLECT', False),
    "RESOURCE_DATA_COLLECT_RATIO": 0.1,
    
    # 缓存
    "DEFAULT_USING_CACHE": "drf_resource.cache.DefaultUsingCache",
}
```

**配置项优先级**（改造后）:
```python
# drf_resource/settings.py
# 优先级：DRF_RESOURCE > settings
APP_CODE = (
    resource_settings.APP_CODE  # 1. 从 DRF_RESOURCE 读取
    or getattr(settings, 'APP_CODE', None)  # 2. 降级到 settings
)
```

#### 向后兼容方案

**完全兼容模式**（推荐）:
```python
# 在 bkmonitor 中，将所有蓝鲸特定配置映射到 DRF_RESOURCE
DRF_RESOURCE = {
    # 自动从 settings 读取，保持兼容
    "APP_CODE": settings.APP_CODE,
    "APP_SECRET": settings.SECRET_KEY,
    "BK_API_MODE": True,
    "BK_IAM_SAAS_HOST": getattr(settings, 'BK_IAM_SAAS_HOST', None),
    "ROLE": getattr(settings, 'ROLE', 'web'),
    
    # 保持原有行为
    "HTTP_AUTH_ENABLED": False,
}
```

**最小适配模式**（快速适配）:
```python
# 仅添加必要的配置项
DRF_RESOURCE = {
    "APP_CODE": settings.APP_CODE,
    "APP_SECRET": settings.SECRET_KEY,
    "BK_API_MODE": True,
}
```

---

### 2. OpenTelemetry 可选依赖 ⚠️ **中影响**

#### 变更内容

OpenTelemetry 从必选依赖改为可选依赖，提供 no-op 降级实现。

#### bkmonitor 影响

**影响程度**: ⚠️ **中影响**

**需要适配的内容**:

1. **依赖管理**（如 bkmonitor 使用 OpenTelemetry）:
   ```python
   # bkmonitor/requirements.txt
   # 确保包含 OpenTelemetry
   opentelemetry-api>=1.0
   opentelemetry-sdk>=1.0
   ```

2. **配置启用**（如 bkmonitor 使用 OpenTelemetry）:
   ```python
   # bkmonitor/settings.py
   DRF_RESOURCE = {
       "OPENTELEMETRY_ENABLED": True,  # 明确启用
       # ... 其他配置
   }
   ```

3. **降级行为**:
   - 如果 bkmonitor 未安装 OpenTelemetry，drf_resource 会自动降级
   - 日志中会记录警告：`"OpenTelemetry not available, using no-op tracer"`
   - 不影响核心功能，仅影响观测性

---

## 行为变更影响

### 1. 版权声明变更 ✅ **无影响**

#### 变更内容

所有 `.py` 文件头部的版权声明从蓝鲸特定改为通用 MIT 协议。

**变更前**:
```python
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
```

**变更后**:
```python
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

#### bkmonitor 影响

**影响程度**: ✅ **无影响**

**说明**:
- 版权声明仅影响代码注释和文档
- 不影响任何代码逻辑或功能
- bkmonitor 可以继续使用自己的版权声明

---

### 2. 日志消息变更 ⚠️ **低影响**

#### 变更内容

日志消息中的 "蓝鲸"、"BK_API" 等术语可能改为通用术语。

**变更示例**:
```python
# 改造前
logger.error("【Module: {}】【Action: {}】蓝鲸 API 调用失败", module, action)

# 改造后
logger.error("【Module: {}】【Action: {}】API 调用失败", module, action)
```

#### bkmonitor 影响

**影响程度**: ⚠️ **低影响**

**说明**:
- 日志消息略有变化，但不影响功能
- 建议在 bkmonitor 中添加自己的日志处理器，如需要蓝鲸特定格式

---

## 破坏性变更

### 🔴 无破坏性变更

**重要**: 本次改造设计为完全向后兼容，**没有破坏性变更**。

所有变更都通过以下方式确保兼容：
1. 配置项降级：`DRF_RESOURCE` → `settings.xxx`
2. 错误类别名：`BKAPIError = APIError`
3. 可选依赖降级：OpenTelemetry no-op 实现
4. 行为保持不变：通过配置项维持原有行为

---

## 向后兼容方案

### 推荐适配策略

#### 方案 A：在 bkmonitor 中配置 DRF_RESOURCE（推荐）

**优点**:
- ✅ 零代码修改
- ✅ 利用配置降级机制
- ✅ 升级到新版 drf_resource 无需适配

**步骤**:
```python
# bkmonitor/settings.py
DRF_RESOURCE = {
    # 蓝鲸特定配置
    "APP_CODE": settings.APP_CODE,
    "APP_SECRET": settings.SECRET_KEY,
    "BK_API_MODE": True,
    "BK_IAM_SAAS_HOST": getattr(settings, 'BK_IAM_SAAS_HOST', ''),
    "ROLE": getattr(settings, 'ROLE', 'web'),
    
    # 保持原有行为
    "HTTP_AUTH_ENABLED": False,
    "HTTP_STANDARD_FORMAT": True,
    
    # 资源收集
    "RESOURCE_DATA_COLLECT_ENABLED": getattr(settings, 'ENABLE_RESOURCE_DATA_COLLECT', False),
    "RESOURCE_DATA_COLLECT_RATIO": 0.1,
}
```

---

#### 方案 B：分阶段渐进适配

适用于需要逐步验证的场景。

**阶段 1：最小适配**（1-2 天）
```python
# 仅添加核心配置
DRF_RESOURCE = {
    "APP_CODE": settings.APP_CODE,
    "APP_SECRET": settings.SECRET_KEY,
    "BK_API_MODE": True,
}
```

**阶段 2：完整适配**（1 周）
```python
# 添加所有配置项
DRF_RESOURCE = {
    # ... 核心配置
    
    # 可选配置
    "OPENTELEMETRY_ENABLED": True,
    # ... 其他配置
}
```

**阶段 3：代码更新**（可选，2-4 周）
- 根据测试结果，更新使用 `BKAPIError` 的代码
- 根据需要，更新错误码处理逻辑

---

#### 方案 C：fork drf_resource（不推荐）

适用于需要高度定制的场景。

**步骤**:
1. Fork drf_resource 仓库
2. 将 bkmonitor 定制的版本作为新的基线
3. 后续改造在 fork 版本上进行

**缺点**:
- ❌ 需要维护独立版本
- ❌ 无法获得 drf_resource 官方更新
- ❌ 增加维护成本

---

## 迁移步骤

### 步骤 1：影响评估（1 天）

**目标**: 全面了解改造对 bkmonitor 的影响范围

**任务**:
1. 搜索所有 `BKAPIError` 的使用
   ```bash
   grep -r "BKAPIError" bkmonitor --include="*.py" -l
   ```

2. 搜索所有 `settings.APP_CODE` 的直接使用
   ```bash
   grep -r "settings\.APP_CODE" bkmonitor --include="*.py" -l
   ```

3. 搜索所有 `nested_api` 或 `KernelAPIResource` 的使用
   ```bash
   grep -r "nested_api\|KernelAPIResource" bkmonitor --include="*.py" -l
   ```

4. 搜索所有 `errors/iam` 中错误类的使用
   ```bash
   grep -r "APIPermissionDeniedError\|9900403" bkmonitor --include="*.py" -l
   ```

5. 检查 OpenTelemetry 的使用
   ```bash
   grep -r "opentelemetry\|OpenTelemetry" bkmonitor --include="*.py" -l
   ```

**输出**: 影响评估报告，列出所有需要修改的文件和代码位置

---

### 步骤 2：环境准备（1 天）

**目标**: 确保 bkmonitor 环境准备好适配新版本的 drf_resource

**任务**:
1. 备份当前环境
   ```bash
   # 备份 requirements
   cp bkmonitor/requirements.txt bkmonitor/requirements.txt.backup
   
   # 备份 settings
   cp bkmonitor/settings.py bkmonitor/settings.py.backup
   ```

2. 创建测试环境
   - 在测试分支上进行适配
   - 或使用功能分支进行改造

3. 更新依赖
   ```python
   # bkmonitor/requirements.txt
   # 确保包含所有需要的依赖
   # 如果 bkmonitor 使用 OpenTelemetry，确保包含：
   opentelemetry-api>=1.0
   opentelemetry-sdk>=1.0
   ```

---

### 步骤 3：配置适配（1-2 天）

**目标**: 在 bkmonitor 中添加 `DRF_RESOURCE` 配置

**任务**:
1. 在 `bkmonitor/settings.py` 中添加 `DRF_RESOURCE` 配置
   ```python
   DRF_RESOURCE = {
       "APP_CODE": settings.APP_CODE,
       "APP_SECRET": settings.SECRET_KEY,
       "BK_API_MODE": True,
       "BK_IAM_SAAS_HOST": getattr(settings, 'BK_IAM_SAAS_HOST', ''),
       "ROLE": getattr(settings, 'ROLE', 'web'),
       
       # 保持原有行为
       "HTTP_AUTH_ENABLED": False,
       "HTTP_STANDARD_FORMAT": True,
       
       # 资源收集
       "RESOURCE_DATA_COLLECT_ENABLED": getattr(settings, 'ENABLE_RESOURCE_DATA_COLLECT', False),
       "RESOURCE_DATA_COLLECT_RATIO": 0.1,
   }
   ```

2. 验证配置正确性
   - 确保所有必要的配置项都有值
   - 确保 `APP_CODE` 和 `APP_SECRET` 正确

---

### 步骤 4：代码适配（1-3 天）

**目标**: 更新受影响的代码

**任务**:
1. **如果 BKAPIError 被重命名**:
   - 搜索所有使用 `BKAPIError` 的地方
   - 评估是否需要更新为 `APIError`
   - 如果采用兼容别名方案，则无需修改

2. **如果使用了 nested_api**:
   - 评估 `KernelAPIResource` 的使用场景
   - 决定是否改用 `APIResource` 或自己实现
   - 更新相关导入和实例化代码

3. **更新错误码处理**（如果需要）:
   - 检查是否有代码依赖 `9900403` 等蓝鲸 IAM 错误码
   - 更新为通用的 HTTP 状态码

---

### 步骤 5：测试验证（2-5 天）

**目标**: 确保 bkmonitor 在新版本 drf_resource 下正常运行

**测试清单**:

#### 5.1 单元测试
```bash
# 运行所有单元测试
cd bkmonitor
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v
```

#### 5.2 API 测试
```bash
# 测试所有 API 端点
pytest tests/api/ -v

# 重点测试使用 APIResource 的接口
pytest tests/api/test_api_resources.py -v
```

#### 5.3 回归测试
```bash
# 运行完整回归测试套件
pytest tests/ -v --cov=bkmonitor
```

#### 5.4 手动验证
- [ ] Resource 自动发现正常工作
- [ ] APIResource 调用外部 API 正常
- [ ] 缓存功能正常
- [ ] 异步任务功能正常
- [ ] OpenTelemetry 追踪正常（如果启用）
- [ ] 错误处理和日志正常
- [ ] API Explorer 功能正常

---

### 步骤 6：上线部署（1 天）

**目标**: 将适配后的 bkmonitor 部署到生产环境

**任务**:
1. 代码审查
   - 确保所有改动符合项目规范
   - 确保配置项正确

2. 合并代码
   - 将适配分支合并到主分支
   - 解决任何合并冲突

3. 灰度发布
   - 先在部分环境部署
   - 观察 1-2 天，确认无异常

4. 全量发布
   - 部署到所有环境
   - 监控关键指标

---

## 测试验证

### 测试场景

#### 1. Resource 自动发现测试

**测试目标**: 验证 `api`, `resource`, `adapter` 全局对象正常工作

**测试方法**:
```python
# test_resource_discovery.py
def test_api_discovery():
    # 测试 api 全局对象
    from drf_resource import api
    assert hasattr(api, 'bkdata')
    
    # 测试 resource 全局对象
    from drf_resource import resource
    assert hasattr(resource, 'plugin')
    
    # 测试 adapter 全局对象
    from drf_resource import adapter
    assert hasattr(adapter, 'cc')
```

**预期结果**: ✅ 所有全局对象正常可访问

---

#### 2. APIResource 调用测试

**测试目标**: 验证 APIResource 通过配置正常工作

**测试方法**:
```python
# test_api_resource.py
def test_api_resource_with_config():
    from drf_resource.contrib import APIResource
    
    class TestAPI(APIResource):
        module_name = "test"
        base_url = "http://test.api"
        action = "/test"
        method = "POST"
    
    # 创建实例并调用
    api = TestAPI()
    try:
        result = api.perform_request({})
        print("API 调用成功:", result)
    except Exception as e:
        print("API 调用失败:", e)
```

**预期结果**: ✅ API 调用成功，错误消息包含 "系统" 而非 "蓝鲸"

---

#### 3. 错误处理测试

**测试目标**: 验证错误类正常工作

**测试方法**:
```python
# test_error_handling.py
def test_bkapi_error():
    from drf_resource.errors.api import BKAPIError, APIError
    
    # 测试 BKAPIError（兼容别名）
    try:
        raise BKAPIError(system_name="test", result={"code": "404", "message": "Not found"})
    except APIError as e:
        print("错误捕获成功:", e.message)
    
    # 测试 APIError
    try:
        raise APIError(system_name="test", result={"code": "404", "message": "Not found"})
    except Exception as e:
        print("错误捕获成功:", e.message)
```

**预期结果**: ✅ `BKAPIError` 和 `APIError` 都能正常工作

---

#### 4. OpenTelemetry 降级测试

**测试目标**: 验证未安装 OpenTelemetry 时降级正常

**测试方法**:
```bash
# 方法 1：不安装 opentelemetry
pip uninstall -y opentelemetry-api opentelemetry-sdk

# 运行测试
pytest tests/ -v

# 预期：测试通过，日志中显示降级警告

# 方法 2：安装 opentelemetry
pip install opentelemetry-api opentelemetry-sdk

# 运行测试
pytest tests/ -v

# 预期：测试通过，OpenTelemetry 正常工作
```

**预期结果**: ✅ 无论是否安装 OpenTelemetry，测试都能通过

---

#### 5. 配置降级测试

**测试目标**: 验证配置项降级机制正常

**测试方法**:
```python
# test_config_fallback.py
def test_config_without_drf_resource():
    # 不配置 DRF_RESOURCE，应该从 settings 降级
    from drf_resource.settings import resource_settings
    
    assert resource_settings.APP_CODE == settings.APP_CODE
    assert resource_settings.APP_SECRET == settings.SECRET_KEY

def test_config_with_drf_resource():
    # 配置 DRF_RESOURCE，应该使用配置值
    from django.conf import settings
    settings.DRF_RESOURCE = {
        "APP_CODE": "test_app",
        "APP_SECRET": "test_secret",
    }
    
    from drf_resource.settings import resource_settings
    assert resource_settings.APP_CODE == "test_app"
    assert resource_settings.APP_SECRET == "test_secret"
```

**预期结果**: ✅ 配置降级机制正常工作

---

### 性能测试

**测试目标**: 确保改造不影响性能

**测试场景**:
1. Resource 自动发现性能
2. API 调用性能（APIResource）
3. 缓存读写性能
4. 异步任务执行性能

**测试方法**:
```bash
# 使用性能测试工具
pytest tests/performance/ --benchmark
```

**预期结果**: ✅ 性能与改造前基本一致（±10%）

---

## 常见问题

### Q1: 升级后 APIResource 无法正常工作？

**问题**: 升级到新版 drf_resource 后，`APIResource` 调用外部 API 失败。

**可能原因**:
1. 未配置 `DRF_RESOURCE` 字典
2. `APP_CODE` 或 `APP_SECRET` 配置错误
3. 蓝鲸 API 模式未启用（`BK_API_MODE` 未设置）

**解决方案**:
```python
# 在 bkmonitor/settings.py 中添加
DRF_RESOURCE = {
    "APP_CODE": settings.APP_CODE,
    "APP_SECRET": settings.SECRET_KEY,
    "BK_API_MODE": True,  # 重要：启用蓝鲸 API 模式
}
```

---

### Q2: BKAPIError 导入失败？

**问题**: 升级后，代码报错 `from drf_resource.errors.api import BKAPIError` 失败。

**可能原因**:
- `BKAPIError` 被重命名或删除

**解决方案**:
- 方案 A（推荐）: 使用兼容别名，无需修改代码
  ```python
  from drf_resource.errors.api import BKAPIError  # 仍可用
  ```

- 方案 B: 更新导入
  ```python
  from drf_resource.errors.api import APIError
  
  # 更新代码中的 BKAPIError 为 APIError
  ```

---

### Q3: OpenTelemetry 追踪数据丢失？

**问题**: 升级后，OpenTelemetry 追踪数据没有正常记录。

**可能原因**:
1. 未安装 OpenTelemetry 依赖
2. 未在 `DRF_RESOURCE` 中启用 `OPENTELEMETRY_ENABLED`

**解决方案**:
```python
# 在 bkmonitor/settings.py 中添加
DRF_RESOURCE = {
    "OPENTELEMETRY_ENABLED": True,  # 明确启用
}

# 确保 requirements.txt 中包含
opentelemetry-api>=1.0
opentelemetry-sdk>=1.0
```

---

### Q4: 资源发现失败？

**问题**: 升级后，`api`, `resource`, `adapter` 全局对象为空。

**可能原因**:
1. `DRF_RESOURCE_AUTO_DISCOVERY` 被设置为 `False`
2. `RESOURCE_DIRS` 配置错误
3. Django app 配置问题

**解决方案**:
```python
# 确保 DRF_RESOURCE 配置
DRF_RESOURCE = {
    "AUTO_DISCOVERY": True,  # 启用自动发现
}

# 或者手动指定资源目录
RESOURCE_DIRS = [
    "api",  # 添加 api 目录
]
```

---

### Q5: 如何回滚到旧版本？

**问题**: 升级后发现严重问题，需要回滚。

**解决方案**:

**方案 A - 重新安装旧版本**:
```bash
pip install drf-resource==old_version
```

**方案 B - 使用代码备份**:
```bash
# 恢复 settings.py
cp bkmonitor/settings.py.backup bkmonitor/settings.py

# 恢复 requirements.txt
cp bkmonitor/requirements.txt.backup bkmonitor/requirements.txt

# 重新安装依赖
pip install -r bkmonitor/requirements.txt
```

---

## 附录

### A. 配置项完整清单

| 配置项 | 类型 | 必需 | 默认值 | 说明 | bkmonitor 建议 |
|---------|------|--------|---------|------|-------------|
| APP_CODE | string | ✅ | 应用编码 | `settings.APP_CODE` |
| APP_SECRET | string | ✅ | 应用密钥 | `settings.SECRET_KEY` |
| BK_API_MODE | boolean | ❌ | False | 是否使用蓝鲸 API 模式 | `True` |
| BK_IAM_SAAS_HOST | string | ❌ | None | 蓝鲸 IAM 地址 | `settings.BK_IAM_SAAS_HOST` |
| ROLE | string | ❌ | None | 角色（web/api） | `settings.ROLE` |
| HTTP_AUTH_ENABLED | boolean | ❌ | False | 是否启用 HTTP 认证 | `False` |
| HTTP_AUTH_HEADER | string | ❌ | Authorization | 认证头名称 | 默认值 |
| HTTP_AUTH_PARAMS | dict | ❌ | {} | 认证参数 | 默认值 |
| HTTP_STANDARD_FORMAT | boolean | ❌ | True | 是否使用标准格式 | `True` |
| HTTP_TIMEOUT | int | ❌ | 60 | 超时时间（秒） | 默认值 |
| HTTP_VERIFY_SSL | boolean | ❌ | True | 是否验证 SSL | 默认值 |
| AUTO_DISCOVERY | boolean | ❌ | True | 是否自动发现 Resource | 默认值 |
| RESOURCE_DATA_COLLECT_ENABLED | boolean | ❌ | False | 是否收集请求数据 | `settings.ENABLE_RESOURCE_DATA_COLLECT` |
| RESOURCE_DATA_COLLECT_RATIO | float | ❌ | 0.1 | 采样比例 | 默认值 |
| DEFAULT_USING_CACHE | string | ❌ | DefaultUsingCache | 默认缓存类 | 默认值 |
| CELERY_QUEUE | string | ❌ | celery_resource | Celery 队列名 | 默认值 |
| OPENTELEMETRY_ENABLED | boolean | ❌ | False | 是否启用 OpenTelemetry | `True`（如使用） |

---

### B. 文件变更清单

| 文件路径 | 变更类型 | 影响程度 | bkmonitor 需要操作 |
|---------|---------|---------|------------------|
| drf_resource/contrib/api.py | 配置化 | ⚠️ 高 | 添加 DRF_RESOURCE 配置 |
| drf_resource/errors/api.py | 类重命名 | ⚠️ 中 | 更新导入（如采用方案 A） |
| drf_resource/contrib/nested_api.py | 删除 | ✅ 无 | 无操作 |
| drf_resource/errors/iam.py | 删除或修改 | ⚠️ 低 | 验证错误码使用 |
| drf_resource/base.py | OpenTelemetry 降级 | ⚠️ 中 | 添加依赖（如使用） |
| drf_resource/exceptions.py | OpenTelemetry 降级 | ⚠️ 中 | 添加依赖（如使用） |
| drf_resource/settings.py | 扩展配置 | ⚠️ 高 | 添加 DRF_RESOURCE 配置 |
| drf_resource/[所有文件] | 版权更新 | ✅ 低 | 无操作 |
| pyproject.toml | 包配置 | ⚠️ 高 | 更新依赖 |
| requirements.txt | 依赖清单 | ⚠️ 高 | 确保包含所需依赖 |

---

### C. 建议的 bkmonitor/settings.py 模板

```python
# -*- coding: utf-8 -*-
"""
BKMonitor settings
"""

from .base_settings import *

# ===== drf_resource 配置 =====
DRF_RESOURCE = {
    # ========== 核心配置（必选）==========
    # 蓝鲸应用信息
    "APP_CODE": APP_CODE,
    "APP_SECRET": SECRET_KEY,
    
    # ========== 蓝鲸特定配置 ==========
    "BK_API_MODE": True,  # 启用蓝鲸 API 模式
    "BK_IAM_SAAS_HOST": BK_IAM_SAAS_HOST,
    "ROLE": getattr(settings, 'ROLE', 'web'),
    
    # ========== 通用配置 ==========
    # HTTP 配置（不启用通用认证，使用蓝鲸模式）
    "HTTP_AUTH_ENABLED": False,
    "HTTP_AUTH_HEADER": "Authorization",
    "HTTP_AUTH_PARAMS": {},
    "HTTP_STANDARD_FORMAT": True,
    "HTTP_TIMEOUT": 60,
    "HTTP_VERIFY_SSL": True,
    
    # ========== 资源配置 ==========
    "AUTO_DISCOVERY": True,
    "RESOURCE_DATA_COLLECT_ENABLED": ENABLE_RESOURCE_DATA_COLLECT,
    "RESOURCE_DATA_COLLECT_RATIO": 0.1,
    "DEFAULT_USING_CACHE": "drf_resource.cache.DefaultUsingCache",
    
    # ========== 异步任务配置 ==========
    "CELERY_QUEUE": "celery_resource",
    
    # ========== 可观测性配置 ==========
    # 如果 bkmonitor 使用了 OpenTelemetry，设置为 True
    "OPENTELEMETRY_ENABLED": True,
}
```

---

## 联系与支持

- **drf_resource 问题**: [GitHub Issues](https://github.com/your-org/drf-resource/issues)
- **bkmonitor 支持**: 联系 bkmonitor 开发团队
- **文档**: [drf-resource.readthedocs.io](https://drf-resource.readthedocs.io)

---

**文档结束**

---

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|-------|--------|---------|------|
| v0.1.0 | 2025-01-12 | 初始版本，记录 drf_resource 通用化改造影响 | DRF Resource Team |
