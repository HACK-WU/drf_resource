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

from unittest.mock import Mock

from drf_resource.api_explorer.permissions import IsTestEnvironment, is_test_environment


class TestIsTestEnvironment:
    """测试 is_test_environment 函数"""

    def test_explicit_enabled(self, mock_settings_api_explorer_enabled):
        """测试显式启用 API Explorer"""
        assert is_test_environment() is True

    def test_explicit_disabled(
        self, mock_settings_api_explorer_disabled, mock_debug_mode
    ):
        """测试显式禁用优先级高于 DEBUG 模式"""
        # 即使 DEBUG=True，显式禁用也会生效
        assert is_test_environment() is False

    def test_debug_mode_enabled(self, mock_debug_mode):
        """测试 DEBUG 模式启用"""
        assert is_test_environment() is True

    def test_debug_mode_disabled(self, mock_production_mode):
        """测试生产环境（DEBUG=False）"""
        assert is_test_environment() is False

    def test_env_dev(self, mock_production_mode, mock_env_dev):
        """测试开发环境变量"""
        assert is_test_environment() is True

    def test_env_test(self, mock_production_mode, monkeypatch):
        """测试测试环境变量"""
        monkeypatch.setenv("ENV", "test")
        assert is_test_environment() is True

    def test_env_local(self, mock_production_mode, monkeypatch):
        """测试本地环境变量"""
        monkeypatch.setenv("ENV", "local")
        assert is_test_environment() is True

    def test_env_production(self, mock_production_mode, mock_env_production):
        """测试生产环境变量"""
        assert is_test_environment() is False

    def test_priority_order(
        self, mock_settings_api_explorer_disabled, mock_debug_mode, mock_env_dev
    ):
        """测试优先级顺序：显式配置 > DEBUG > ENV"""
        # 显式配置为 False，即使 DEBUG 和 ENV 都指向测试环境
        assert is_test_environment() is False


class TestIsTestEnvironmentPermission:
    """测试 IsTestEnvironment 权限类"""

    def test_has_permission_allowed(self, mock_settings_api_explorer_enabled):
        """测试权限检查通过"""
        permission = IsTestEnvironment()
        mock_request = Mock()
        mock_view = Mock()

        assert permission.has_permission(mock_request, mock_view) is True

    def test_has_permission_denied(self, mock_production_mode, mock_env_production):
        """测试权限检查不通过"""
        permission = IsTestEnvironment()
        mock_request = Mock()
        mock_view = Mock()

        assert permission.has_permission(mock_request, mock_view) is False

    def test_has_object_permission_allowed(self, mock_settings_api_explorer_enabled):
        """测试对象级权限检查通过"""
        permission = IsTestEnvironment()
        mock_request = Mock()
        mock_view = Mock()
        mock_obj = Mock()

        assert (
            permission.has_object_permission(mock_request, mock_view, mock_obj) is True
        )

    def test_has_object_permission_denied(
        self, mock_production_mode, mock_env_production
    ):
        """测试对象级权限检查不通过"""
        permission = IsTestEnvironment()
        mock_request = Mock()
        mock_view = Mock()
        mock_obj = Mock()

        assert (
            permission.has_object_permission(mock_request, mock_view, mock_obj) is False
        )

    def test_object_permission_consistency(self, mock_debug_mode):
        """测试对象级权限与普通权限的一致性"""
        permission = IsTestEnvironment()
        mock_request = Mock()
        mock_view = Mock()
        mock_obj = Mock()

        # 两个权限检查应该返回相同的结果
        has_perm = permission.has_permission(mock_request, mock_view)
        has_obj_perm = permission.has_object_permission(
            mock_request, mock_view, mock_obj
        )

        assert has_perm == has_obj_perm
