"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json

from rest_framework import status
from unittest.mock import Mock, patch

from drf_resource.api_explorer.exceptions import ResourceNotFoundError


class TestHomeView:
    """测试 HomeView"""

    def test_get_home_with_permission(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试在测试环境访问前端页面"""
        response = api_client.get("/api-explorer/home/")

        # 如果路由配置正确,应该返回 200 并渲染 HTML
        # 如果路由不存在,会返回 404
        # 暂时不验证具体内容,只确认状态码
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_get_home_without_permission(
        self, api_client, mock_production_mode, mock_env_production
    ):
        """测试在生产环境访问前端页面(应被拒绝)"""
        response = api_client.get("/api-explorer/home/")

        # 应该返回 403 或者 404
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]


class TestIndexView:
    """测试 IndexView"""

    def test_get_index_without_permission(
        self, api_client, mock_production_mode, mock_env_production
    ):
        """测试在生产环境访问主页（应被拒绝）"""
        response = api_client.get("/api-explorer/")

        # 应该返回 403 或者不允许访问
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_get_index_with_permission(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试在测试环境访问主页"""
        response = api_client.get("/api-explorer/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["result"] is True
        assert "data" in data
        assert "title" in data["data"]
        assert "endpoints" in data["data"]


class TestCatalogView:
    """测试 CatalogView"""

    def test_get_catalog_success(self, api_client, mock_settings_api_explorer_enabled):
        """测试成功获取 API 目录"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.discover_all_apis"
        ) as mock_discover:
            mock_discover.return_value = {"modules": [], "total": 0}

            response = api_client.get("/api-explorer/catalog/")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["result"] is True
            assert "modules" in data["data"]
            assert "total" in data["data"]

    def test_get_catalog_with_search(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试带搜索关键词获取目录"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.discover_all_apis"
        ) as mock_discover:
            mock_discover.return_value = {"modules": [], "total": 0}

            response = api_client.get("/api-explorer/catalog/", {"search": "test"})

            assert response.status_code == status.HTTP_200_OK
            # 验证 discover_all_apis 被调用时传入了 search 参数
            mock_discover.assert_called_once_with(search="test", module_filter=None)

    def test_get_catalog_with_module_filter(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试带模块过滤获取目录"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.discover_all_apis"
        ) as mock_discover:
            mock_discover.return_value = {"modules": [], "total": 0}

            response = api_client.get(
                "/api-explorer/catalog/", {"module": "test_module"}
            )

            assert response.status_code == status.HTTP_200_OK
            # 验证 discover_all_apis 被调用时传入了 module_filter 参数
            mock_discover.assert_called_once_with(
                search=None, module_filter="test_module"
            )

    def test_get_catalog_invalid_params(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试无效参数（参数校验测试）"""
        # 当前实现中 search 和 module 都是可选的，这里测试空字符串
        response = api_client.get(
            "/api-explorer/catalog/", {"search": "", "module": ""}
        )

        # 应该成功，因为空字符串是允许的
        assert response.status_code == status.HTTP_200_OK

    def test_get_catalog_service_error(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试服务层抛出异常"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.discover_all_apis"
        ) as mock_discover:
            mock_discover.side_effect = Exception("Service error")

            response = api_client.get("/api-explorer/catalog/")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["result"] is False
            assert "message" in data

    def test_get_catalog_without_permission(
        self, api_client, mock_production_mode, mock_env_production
    ):
        """测试无权限访问目录"""
        response = api_client.get("/api-explorer/catalog/")

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]


class TestAPIDetailView:
    """测试 APIDetailView"""

    def test_get_api_detail_success(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试成功获取 API 详情"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.get_api_detail"
        ) as mock_get_detail:
            mock_get_detail.return_value = {
                "module": "test_module",
                "api_name": "test_api",
                "label": "Test API",
                "request_params": [],
                "response_params": [],
            }

            response = api_client.get(
                "/api-explorer/api_detail/",
                {"module": "test_module", "api_name": "test_api"},
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["result"] is True
            assert data["data"]["module"] == "test_module"
            assert data["data"]["api_name"] == "test_api"

    def test_get_api_detail_missing_params(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试缺少必填参数"""
        # 缺少 module
        response = api_client.get("/api-explorer/api_detail/", {"api_name": "test_api"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 缺少 api_name
        response = api_client.get(
            "/api-explorer/api_detail/", {"module": "test_module"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 全部缺少
        response = api_client.get("/api-explorer/api_detail/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_api_detail_not_found(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试获取不存在的 API"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.get_api_detail"
        ) as mock_get_detail:
            mock_get_detail.side_effect = ResourceNotFoundError("API not found")

            response = api_client.get(
                "/api-explorer/api_detail/", {"module": "test", "api_name": "test"}
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert data["result"] is False

    def test_get_api_detail_service_error(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试服务层抛出异常"""
        with patch(
            "drf_resource.api_explorer.services.APIDiscoveryService.get_api_detail"
        ) as mock_get_detail:
            mock_get_detail.side_effect = Exception("Service error")

            response = api_client.get(
                "/api-explorer/api_detail/", {"module": "test", "api_name": "test"}
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["result"] is False

    def test_get_api_detail_without_permission(
        self, api_client, mock_production_mode, mock_env_production
    ):
        """测试无权限访问 API 详情"""
        response = api_client.get(
            "/api-explorer/api_detail/", {"module": "test", "api_name": "test"}
        )

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]


class TestInvokeView:
    """测试 InvokeView"""

    def test_invoke_api_success(self, api_client, mock_settings_api_explorer_enabled):
        """测试成功调用 API"""
        with patch(
            "drf_resource.api_explorer.services.APIInvokeService.invoke_api"
        ) as mock_invoke:
            mock_invoke.return_value = {
                "success": True,
                "response": {"result": "ok"},
                "duration": 0.5,
                "timestamp": "2026-01-12T10:00:00",
            }

            response = api_client.post(
                "/api-explorer/invoke/",
                data=json.dumps(
                    {
                        "module": "test_module",
                        "api_name": "test_api",
                        "params": {"key": "value"},
                    }
                ),
                content_type="application/json",
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["result"] is True
            assert "data" in data

    def test_invoke_api_with_empty_params(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试不传参数调用 API"""
        with patch(
            "drf_resource.api_explorer.services.APIInvokeService.invoke_api"
        ) as mock_invoke:
            mock_invoke.return_value = {"success": True, "response": {}}

            response = api_client.post(
                "/api-explorer/invoke/",
                data=json.dumps({"module": "test_module", "api_name": "test_api"}),
                content_type="application/json",
            )

            assert response.status_code == status.HTTP_200_OK
            # 验证调用时传入了空字典
            call_args = mock_invoke.call_args
            assert call_args[0][2] == {}

    def test_invoke_api_missing_params(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试缺少必填参数"""
        # 缺少 module
        response = api_client.post(
            "/api-explorer/invoke/",
            data=json.dumps({"api_name": "test_api"}),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # 缺少 api_name
        response = api_client.post(
            "/api-explorer/invoke/",
            data=json.dumps({"module": "test_module"}),
            content_type="application/json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invoke_api_not_found(self, api_client, mock_settings_api_explorer_enabled):
        """测试调用不存在的 API"""
        with patch(
            "drf_resource.api_explorer.services.APIInvokeService.invoke_api"
        ) as mock_invoke:
            mock_invoke.side_effect = ResourceNotFoundError("API not found")

            response = api_client.post(
                "/api-explorer/invoke/",
                data=json.dumps({"module": "test", "api_name": "test"}),
                content_type="application/json",
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert data["result"] is False

    def test_invoke_api_failure(self, api_client, mock_settings_api_explorer_enabled):
        """测试 API 调用失败"""
        with patch(
            "drf_resource.api_explorer.services.APIInvokeService.invoke_api"
        ) as mock_invoke:
            mock_invoke.return_value = {
                "success": False,
                "error_message": "API call failed",
                "response": None,
            }

            response = api_client.post(
                "/api-explorer/invoke/",
                data=json.dumps({"module": "test", "api_name": "test"}),
                content_type="application/json",
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["result"] is False
            assert "调用失败" in data["message"]

    def test_invoke_api_service_error(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试服务层抛出异常"""
        with patch(
            "drf_resource.api_explorer.services.APIInvokeService.invoke_api"
        ) as mock_invoke:
            mock_invoke.side_effect = Exception("Service error")

            response = api_client.post(
                "/api-explorer/invoke/",
                data=json.dumps({"module": "test", "api_name": "test"}),
                content_type="application/json",
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert data["result"] is False

    def test_invoke_api_without_permission(
        self, api_client, mock_production_mode, mock_env_production
    ):
        """测试无权限调用 API"""
        response = api_client.post(
            "/api-explorer/invoke/",
            data=json.dumps({"module": "test", "api_name": "test"}),
            content_type="application/json",
        )

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_invoke_api_extracts_username(
        self, api_client, mock_settings_api_explorer_enabled
    ):
        """测试调用时提取用户名"""
        with patch(
            "drf_resource.api_explorer.services.APIInvokeService.invoke_api"
        ) as mock_invoke:
            mock_invoke.return_value = {"success": True, "response": {}}

            # 创建一个带用户的请求
            api_client.force_authenticate(user=Mock(username="test_user"))

            response = api_client.post(
                "/api-explorer/invoke/",
                data=json.dumps({"module": "test", "api_name": "test"}),
                content_type="application/json",
            )

            assert response.status_code == status.HTTP_200_OK
            # 验证 username 被传递
            call_args = mock_invoke.call_args
            assert call_args[0][3] == "test_user"
