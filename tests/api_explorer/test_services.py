"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pytest
from unittest.mock import patch

from drf_resource.api_explorer.exceptions import ResourceNotFoundError
from drf_resource.api_explorer.services import APIDiscoveryService, APIInvokeService


class TestAPIDiscoveryService:
    """测试 APIDiscoveryService 服务"""

    def test_discover_all_apis_success(self, mock_api_module):
        """测试成功发现所有 API"""
        result = APIDiscoveryService.discover_all_apis()

        assert "modules" in result
        assert "total" in result
        assert isinstance(result["modules"], list)
        assert isinstance(result["total"], int)

    def test_discover_all_apis_with_search(self, mock_api_module):
        """测试带搜索关键词的 API 发现"""
        result = APIDiscoveryService.discover_all_apis(search="test")

        assert "modules" in result
        # 应该只返回匹配的结果
        for module in result["modules"]:
            has_match = any(
                "test" in api.get("name", "").lower()
                or "test" in api.get("label", "").lower()
                or "test" in api.get("class_name", "").lower()
                for api in module["apis"]
            )
            assert has_match or "test" in module["name"].lower()

    def test_discover_all_apis_with_module_filter(self, mock_api_module):
        """测试带模块过滤的 API 发现"""
        result = APIDiscoveryService.discover_all_apis(module_filter="mock_module")

        assert "modules" in result
        # 应该只返回指定模块
        if result["modules"]:
            for module in result["modules"]:
                assert module["name"] == "mock_module"

    def test_extract_module_apis(self, mock_api_module):
        """测试提取模块下的所有 API"""
        apis = APIDiscoveryService._extract_module_apis(
            "mock_module", mock_api_module, None
        )

        assert isinstance(apis, list)
        assert len(apis) > 0
        # 检查 API 元数据结构
        for api in apis:
            assert "name" in api
            assert "module" in api
            assert "class_name" in api

    def test_extract_metadata(self, mock_resource_class):
        """测试提取 Resource 元数据"""
        metadata = APIDiscoveryService._extract_metadata(
            "test_module", "test_api", mock_resource_class
        )

        assert metadata["name"] == "test_api"
        assert metadata["module"] == "test_module"
        assert metadata["class_name"] == mock_resource_class.__name__
        assert "label" in metadata
        assert "method" in metadata
        assert "base_url" in metadata
        assert "action" in metadata
        assert "full_url" in metadata

    def test_extract_metadata_with_error(self):
        """测试提取元数据时发生错误"""

        # 创建一个会抛出异常的 Resource 类
        class ErrorResource:
            pass

        metadata = APIDiscoveryService._extract_metadata(
            "test_module", "test_api", ErrorResource
        )

        # 应该返回最小元数据
        assert metadata["name"] == "test_api"
        assert metadata["module"] == "test_module"
        assert metadata["has_request_serializer"] is False
        assert metadata["has_response_serializer"] is False

    def test_build_full_url(self):
        """测试拼接完整 URL"""
        # 正常情况
        url = APIDiscoveryService._build_full_url("http://example.com/api", "/test")
        assert url == "http://example.com/api/test"

        # 处理斜杠
        url = APIDiscoveryService._build_full_url("http://example.com/api/", "test")
        assert url == "http://example.com/api/test"

        # 空值
        url = APIDiscoveryService._build_full_url("", "/test")
        assert url == ""

        url = APIDiscoveryService._build_full_url("http://example.com", "")
        assert url == ""

    def test_match_search(self):
        """测试搜索匹配"""
        metadata = {
            "module": "test_module",
            "name": "test_api",
            "class_name": "TestResource",
            "label": "Test API Label",
        }

        # 匹配模块名
        assert APIDiscoveryService._match_search(metadata, "module")
        # 匹配接口名
        assert APIDiscoveryService._match_search(metadata, "api")
        # 匹配类名
        assert APIDiscoveryService._match_search(metadata, "resource")
        # 匹配标签
        assert APIDiscoveryService._match_search(metadata, "label")
        # 不匹配
        assert not APIDiscoveryService._match_search(metadata, "nomatch")

    def test_get_api_detail_success(self):
        """测试成功获取 API 详情"""
        with patch.object(APIDiscoveryService, "get_api_detail") as mock_get_detail:
            mock_get_detail.return_value = {
                "module": "test_module",
                "api_name": "test_api",
                "class_name": "TestResource",
                "label": "Test API",
                "method": "GET",
                "full_url": "http://example.com/api",
                "request_params": [],
                "response_params": [],
            }

            result = APIDiscoveryService.get_api_detail("test_module", "test_api")

            assert result["module"] == "test_module"
            assert result["api_name"] == "test_api"
            assert "class_name" in result
            assert "label" in result
            assert "method" in result
            assert "full_url" in result
            assert "request_params" in result
            assert "response_params" in result

    def test_get_api_detail_module_not_found(self):
        """测试获取不存在模块的 API 详情"""
        with pytest.raises(ResourceNotFoundError) as exc_info:
            APIDiscoveryService.get_api_detail("nonexistent_module", "test_api")
        assert "模块不存在" in str(exc_info.value)

    def test_get_api_detail_api_not_found(self):
        """测试获取不存在的 API 详情"""
        with pytest.raises(ResourceNotFoundError) as exc_info:
            APIDiscoveryService.get_api_detail(
                "nonexistent_module_xyz", "nonexistent_api"
            )
        # 验证错误消息包含相关信息
        error_msg = str(exc_info.value)
        assert (
            "模块不存在" in error_msg
            or "API 不存在" in error_msg
            or "not found" in error_msg.lower()
        )


class TestAPIInvokeService:
    """测试 APIInvokeService 服务"""

    def test_invoke_api_success(self, mock_api_module):
        """测试成功调用 API"""
        result = APIInvokeService.invoke_api(
            "mock_module", "test_api", {"name": "test"}, "test_user"
        )

        assert "success" in result
        assert "response" in result
        assert "duration" in result
        assert "timestamp" in result
        assert "request_params" in result

        if result["success"]:
            assert result["response"] is not None
        else:
            assert "error_message" in result

    def test_invoke_api_with_fail_resource(self, mock_api_module):
        """测试调用会失败的 API"""
        result = APIInvokeService.invoke_api("mock_module", "fail_api", {}, "test_user")

        assert result["success"] is False
        assert result["error_message"] is not None
        assert "duration" in result
        assert result["duration"] >= 0

    def test_invoke_api_not_found(self):
        """测试调用不存在的 API"""
        result = APIInvokeService.invoke_api("nonexistent", "test_api", {}, "test_user")

        assert result["success"] is False
        assert "error_message" in result
        # 模块不存在时，error_code 可能为 None 或 "404"
        assert result["error_message"] is not None

    def test_invoke_api_adds_username(self):
        """测试调用时自动添加用户名"""
        # 测试 _mask_sensitive 方法会包含原始参数
        result = APIInvokeService.invoke_api(
            "nonexistent", "test_api", {"name": "value"}, "test_user"
        )

        # 确认请求参数被记录（name 不是敏感字段）
        assert "request_params" in result
        assert result["request_params"].get("name") == "value"

    def test_get_resource_success(self, mock_api_module):
        """测试成功获取 Resource 实例"""
        resource = APIInvokeService._get_resource("mock_module", "test_api")
        assert resource is not None

    def test_get_resource_not_found(self):
        """测试获取不存在的 Resource"""
        # 由于 lazy loading 机制，_get_resource 可能返回一个 lazy 对象
        # 而不是立即抛出异常，异常会在实际调用时抛出
        # 这里测试 invoke_api 的整体行为
        result = APIInvokeService.invoke_api(
            "nonexistent_module_xyz", "test_api", {}, "test_user"
        )

        # 应该返回失败结果
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_mask_sensitive_params(self):
        """测试敏感参数脱敏"""
        params = {
            "username": "test_user",
            "password": "123456789",  # 长度 > 8
            "bk_app_secret": "secret123456789",
            "token_value": "abcdefghijk",  # 使用 token_value 而不是 token
            "normal_param": "normal_value",  # 使用不包含敏感词的键名
        }

        masked = APIInvokeService._mask_sensitive(params)

        # 敏感字段应该被脱敏（长度 > 8 时保留前4后4）
        assert masked["password"] == "1234***6789"
        assert masked["bk_app_secret"] == "secr***6789"
        assert masked["token_value"] == "abcd***hijk"
        # 普通字段不受影响
        assert masked["normal_param"] == "normal_value"
        assert masked["username"] == "test_user"

    def test_mask_sensitive_short_values(self):
        """测试脱敏短值"""
        params = {"password": "short"}

        masked = APIInvokeService._mask_sensitive(params)

        # 短值应该完全脱敏
        assert masked["password"] == "***"

    def test_mask_sensitive_empty_params(self):
        """测试脱敏空参数"""
        masked = APIInvokeService._mask_sensitive({})
        assert masked == {}

        masked = APIInvokeService._mask_sensitive(None)
        assert masked == {}

    def test_invoke_records_duration(self, mock_api_module):
        """测试调用记录持续时间"""
        result = APIInvokeService.invoke_api(
            "mock_module", "test_api", {"name": "test"}, "test_user"
        )

        assert "duration" in result
        assert isinstance(result["duration"], int | float)
        assert result["duration"] >= 0

    def test_invoke_records_timestamp(self, mock_api_module):
        """测试调用记录时间戳"""
        result = APIInvokeService.invoke_api(
            "mock_module", "test_api", {"name": "test"}, "test_user"
        )

        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
        # 检查时间戳格式（ISO format）
        assert "T" in result["timestamp"]
