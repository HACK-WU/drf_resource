# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from drf_resource.base import Resource
from drf_resource.management.root import adapter, api, resource
from drf_resource.decorators import (
    register_resource,
    register_function,
    register_as,
    conditional_register,
    batch_register,
    unregister_resource,
    list_registered_resources,
    get_resource_info,
)
from drf_resource.registry import resource_registry

# 延迟导入 contrib 模块以避免 Django 依赖
APIResource = None
CacheResource = None

def _load_contrib_classes():
    """延迟加载 contrib 类"""
    global APIResource, CacheResource
    if APIResource is None or CacheResource is None:
        try:
            from drf_resource.contrib import APIResource as _APIResource, CacheResource as _CacheResource
            APIResource = _APIResource
            CacheResource = _CacheResource
        except ImportError:
            pass
    return APIResource, CacheResource

# 动态属性访问
def __getattr__(name):
    if name == 'APIResource':
        api_res, _ = _load_contrib_classes()
        return api_res
    elif name == 'CacheResource':
        _, cache_res = _load_contrib_classes()
        return cache_res
    raise AttributeError(f"module '{__name__}' has no attribute '{name__}'")

__author__ = "蓝鲸智云"
__copyright__ = "Copyright (c)   2012-2021 Tencent BlueKing. All Rights Reserved."
__doc__ = """
自动发现项目下resource和adapter和api
    cc
    ├── adapter
    │   ├── default.py
    │   ├── community
    │   │   └── resources.py
    │   └── enterprise
    │       └── resources.py
    └── resources.py
    使用:
        resource.cc -> cc/resources.py
        # 调用resource.cc 即可访问对应文件下的resource
        adapter.cc -> cc/adapter/default.py -> cc/adapter/${platform}/resources.py
        # 调用adapter.cc 既可访问对应文件下的resource，
        # 如果在${platform}/resources.py里面有相同定义，会重载default.py下的resource
    """
__all__ = [
    "Resource", 
    "adapter", 
    "api", 
    "resource",
    "register_resource",
    "register_function",
    "register_as",
    "conditional_register",
    "batch_register",
    "unregister_resource",
    "list_registered_resources",
    "get_resource_info",
    "resource_registry",
    "APIResource",
    "CacheResource",
]
