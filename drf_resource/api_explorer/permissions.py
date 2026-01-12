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

import os

from django.conf import settings
from rest_framework.permissions import BasePermission


def is_test_environment():
    """
    判断是否为测试环境
    
    判断依据（优先级从高到低）：
    1. 显式配置：settings.DRF_RESOURCE['API_EXPLORER_ENABLED']
    2. DEBUG 模式：settings.DEBUG == True
    3. 环境变量：ENV in ['dev', 'test', 'development', 'testing', 'local']
    4. 默认禁用
    
    Returns:
        bool: 是否为测试环境
    """
    # 优先级1：显式配置
    if hasattr(settings, 'DRF_RESOURCE'):
        explicit = settings.DRF_RESOURCE.get('API_EXPLORER_ENABLED')
        if explicit is not None:
            return explicit
    
    # 优先级2：DEBUG 模式
    if hasattr(settings, 'DEBUG') and settings.DEBUG:
        return True
    
    # 优先级3：环境变量
    env = os.getenv('ENV', '').lower()
    if env in ['dev', 'test', 'development', 'testing', 'local']:
        return True
    
    # 默认禁用
    return False


class IsTestEnvironment(BasePermission):
    """
    权限类：仅在测试环境允许访问
    """
    
    def has_permission(self, request, view):
        """
        检查是否为测试环境
        
        Args:
            request: Django request 对象
            view: 视图对象
            
        Returns:
            bool: 是否允许访问
        """
        return is_test_environment()
    
    def has_object_permission(self, request, view, obj):
        """
        对象级权限检查（与 has_permission 保持一致）
        """
        return self.has_permission(request, view)
