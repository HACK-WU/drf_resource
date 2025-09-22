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
from drf_resource.contrib import APIResource, CacheResource
from drf_resource.decorators import (
    batch_register,
    conditional_register,
    get_resource_info,
    list_registered_resources,
    register_as,
    register_function,
    register_resource,
    unregister_resource,
)
from drf_resource.management.root import adapter, api, resource
from drf_resource.registry import resource_registry

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
