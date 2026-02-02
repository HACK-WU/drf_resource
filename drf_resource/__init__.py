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
DRF-Resource 框架

一个基于 Django REST Framework 的声明式 API 资源框架。

核心模块:
    - resources: Resource 核心类 (Resource, APIResource, CacheResource)
    - views: 视图相关 (ResourceViewSet, ResourceRoute, ResourceRouter)
    - response: 响应处理 (ResponseFormatter, ResourceJSONRenderer)
    - exceptions: 异常体系
    - tasks: 异步任务
    - utils: 工具函数
    - contrib: 第三方集成 (spectacular)

基本用法:
    from drf_resource import Resource, APIResource, CacheResource

    class MyResource(Resource):
        def perform_request(self, validated_request_data):
            return {"result": "success"}

    # 调用
    result = MyResource().request({"param": "value"})
"""

# Resource 核心类（新位置：resources/）
from drf_resource.resources import (
    Resource,
    APIResource,
    APICacheResource,
    CacheResource,
    CacheTypeItem,
    using_cache,
)

# 视图相关（新位置：views/）
from drf_resource.views import (
    ResourceViewSet,
    ResourceRoute,
    ResourceRouter,
)

# 响应处理（新位置：response/）
from drf_resource.response import (
    ResourceJSONRenderer,
    ResponseFormatter,
    BaseResponseFormatter,
)

# 自动发现管理
from drf_resource.management.root import adapter, api, resource

__author__ = "蓝鲸智云"
__copyright__ = "Copyright (c) 2012-2021 Tencent BlueKing. All Rights Reserved."
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
    # Resource 核心类
    "Resource",
    "APIResource",
    "APICacheResource",
    "CacheResource",
    # 缓存相关
    "CacheTypeItem",
    "using_cache",
    # 视图相关
    "ResourceViewSet",
    "ResourceRoute",
    "ResourceRouter",
    # 响应处理
    "ResourceJSONRenderer",
    "ResponseFormatter",
    "BaseResponseFormatter",
    # 自动发现
    "adapter",
    "api",
    "resource",
]
