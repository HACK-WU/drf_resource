"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

"""
Resource 核心模块

本模块提供了 drf_resource 的核心类：
    - Resource: 基础 Resource 类
    - APIResource: HTTP API 客户端 Resource
    - APICacheResource: 带缓存的 HTTP API 客户端 Resource
    - CacheResource: 支持缓存的 Resource Mixin

缓存相关:
    - CacheTypeItem: 缓存类型定义
    - using_cache: 缓存装饰器
"""

from drf_resource.resources.base import Resource
from drf_resource.resources.cache import (
    CacheResource,
    CacheTypeItem,
    BaseCacheType,
    DefaultCacheType,
    using_cache,
)
from drf_resource.resources.api import (
    APIResource,
    APICacheResource,
    BKAPIError,
)

__all__ = [
    # Resource 核心类
    "Resource",
    "APIResource",
    "APICacheResource",
    "CacheResource",
    # 缓存相关
    "CacheTypeItem",
    "BaseCacheType",
    "DefaultCacheType",
    "using_cache",
    # 错误类型（向后兼容）
    "BKAPIError",
]
