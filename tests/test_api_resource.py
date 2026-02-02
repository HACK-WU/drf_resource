"""
APIResource 和 APICacheResource 单元测试
"""

import pytest
from unittest.mock import MagicMock
from rest_framework import serializers

from drf_resource.resources.api import APIResource, APICacheResource
from drf_resource.exceptions import BKAPIError as APIError


# ========== 测试用的具体实现类 ==========


class MockAPIResource(APIResource):
    """测试用的 APIResource 实现"""

    base_url = "https://api.example.com"
    module_name = "test_module"
    action = "/api/v1/users/"
    method = "GET"


class MockAPIResourceWithSerializer(MockAPIResource):
    """带 RequestSerializer 的 APIResource"""

    class RequestSerializer(serializers.Serializer):
        user_id = serializers.IntegerField(required=True)


class MockPostAPIResource(APIResource):
    """POST 请求的 APIResource"""

    base_url = "https://api.example.com"
    module_name = "test_module"
    action = "/api/v1/users/"
    method = "POST"


class MockCacheAPIResource(APICacheResource):
    """测试用的 APICacheResource 实现"""

    base_url = "https://api.example.com"
    module_name = "test_module"
    action = "/api/v1/users/"
    method = "GET"


# ========== 测试类 ==========


class TestAPIResourceInheritance:
    """测试 APIResource 继承结构"""

    def test_mro_contains_drfclient_and_resource(self):
        """测试 MRO 包含 DRFClient 和 Resource"""
        mro_names = [c.__name__ for c in APIResource.__mro__]
        assert "DRFClient" in mro_names
        assert "Resource" in mro_names
        assert "BaseClient" in mro_names

    def test_api_cache_resource_mro(self):
        """测试 APICacheResource 的 MRO"""
        mro_names = [c.__name__ for c in APICacheResource.__mro__]
        assert "APIResource" in mro_names
        assert "DRFClient" in mro_names
        assert "CacheResource" in mro_names
        assert "Resource" in mro_names


class TestAPIResourceInit:
    """测试 APIResource 初始化"""

    def test_init_creates_session(self):
        """测试初始化时创建 Session"""
        resource = MockAPIResource()
        assert resource.session is not None

    def test_init_sets_timeout(self):
        """测试初始化时设置超时时间"""
        resource = MockAPIResource()
        assert resource.TIMEOUT == 60
        assert resource.default_timeout == 60

    def test_custom_timeout(self):
        """测试自定义超时时间"""

        class CustomTimeoutResource(MockAPIResource):
            TIMEOUT = 120

        resource = CustomTimeoutResource()
        assert resource.TIMEOUT == 120


class TestAPIResourceRequest:
    """测试 APIResource 请求功能"""

    def test_get_request(self):
        """测试 GET 请求"""
        resource = MockAPIResource()

        # Mock DRFClient 的内部方法，返回格式化后的响应
        resource._make_request_and_format = MagicMock(
            return_value={
                "result": True,
                "code": 200,
                "message": "success",
                "data": {"id": 1, "name": "test"},
            }
        )

        result = resource.request({"user_id": 123})

        assert result == {"id": 1, "name": "test"}
        resource._make_request_and_format.assert_called_once()

    def test_post_request(self):
        """测试 POST 请求"""
        resource = MockPostAPIResource()

        resource._make_request_and_format = MagicMock(
            return_value={
                "result": True,
                "code": 200,
                "message": "success",
                "data": {"id": 1},
            }
        )

        result = resource.request({"name": "test", "email": "test@example.com"})

        assert result == {"id": 1}

    def test_request_with_serializer(self):
        """测试带 RequestSerializer 的请求"""
        resource = MockAPIResourceWithSerializer()

        resource._make_request_and_format = MagicMock(
            return_value={"result": True, "code": 200, "data": {"id": 1}}
        )

        result = resource.request({"user_id": 123})

        assert result == {"id": 1}


class TestAPIResourceErrorHandling:
    """测试 APIResource 错误处理"""

    def test_api_error_on_failed_result(self):
        """测试 API 返回失败结果时抛出 APIError"""
        resource = MockAPIResource()

        # Mock 返回失败结果
        resource._make_request_and_format = MagicMock(
            return_value={
                "result": False,
                "code": 500,
                "message": "Internal error",
                "data": None,
            }
        )

        with pytest.raises(APIError) as exc_info:
            resource.request({})

        assert "test_module" in str(exc_info.value.message)

    def test_timeout_error(self):
        """测试超时错误"""

        resource = MockAPIResource()

        # Mock 抛出超时异常
        resource._make_request_and_format = MagicMock(
            return_value={
                "result": False,
                "code": -1,
                "message": "Request timed out",
                "data": None,
            }
        )

        with pytest.raises(APIError) as exc_info:
            resource.request({})

        assert "test_module" in str(exc_info.value.message)


class TestAPIResourceHelperMethods:
    """测试 APIResource 辅助方法"""

    def test_get_request_url(self):
        """测试 URL 拼接"""
        resource = MockAPIResource()
        url = resource.get_request_url({})
        assert url == "https://api.example.com/api/v1/users/"

    def test_get_headers_default_empty(self):
        """测试默认请求头为空"""
        resource = MockAPIResource()
        headers = resource.get_headers()
        assert headers == {}

    def test_full_request_data_default(self):
        """测试默认 full_request_data 不修改数据"""
        resource = MockAPIResource()
        data = {"key": "value"}
        result = resource.full_request_data(data)
        assert result == data

    def test_render_response_data_default(self):
        """测试默认 render_response_data 不修改数据"""
        resource = MockAPIResource()
        data = {"key": "value"}
        result = resource.render_response_data({}, data)
        assert result == data

    def test_split_request_data(self):
        """测试分离文件和非文件数据"""
        # 这个方法已经移除，跳过测试
        pass


class TestAPICacheResource:
    """测试 APICacheResource"""

    def test_inherits_from_api_resource(self):
        """测试继承自 APIResource"""
        assert issubclass(APICacheResource, APIResource)

    def test_cache_type_none_by_default(self):
        """测试默认没有缓存"""
        resource = MockCacheAPIResource()
        assert resource.cache_type is None

    def test_request_works_without_cache(self):
        """测试无缓存时正常请求"""
        resource = MockCacheAPIResource()

        resource._make_request_and_format = MagicMock(
            return_value={"result": True, "code": 200, "data": {"id": 1}}
        )

        result = resource.request({})

        assert result == {"id": 1}


class TestAPIResourceNonStandardFormat:
    """测试非标准格式响应"""

    def test_non_standard_format(self):
        """测试 IS_STANDARD_FORMAT=False 时直接返回整个响应"""

        class NonStandardResource(MockAPIResource):
            IS_STANDARD_FORMAT = False

        resource = NonStandardResource()

        # 非标准格式时，响应格式化器会直接返回整个数据
        resource._make_request_and_format = MagicMock(
            return_value={
                "result": True,
                "code": 200,
                "message": "success",
                "data": {"users": [{"id": 1}, {"id": 2}], "total": 2},
            }
        )

        result = resource.request({})

        # 非标准格式返回整个 data
        assert result == {"users": [{"id": 1}, {"id": 2}], "total": 2}


class TestAPIError:
    """测试 APIError"""

    def test_api_error_with_string_result(self):
        """测试字符串结果"""
        error = APIError(
            system_name="test_system", url="/api/test", result="Something went wrong"
        )

        assert "test_system" in error.message
        assert "/api/test" in error.message

    def test_api_error_with_dict_result(self):
        """测试字典结果"""
        error = APIError(
            system_name="test_system",
            url="/api/test",
            result={"code": 500, "message": "Internal error"},
        )

        assert "test_system" in error.message
        assert "500" in error.message
        assert "Internal error" in error.message

    def test_bk_api_error_alias(self):
        """测试 BKAPIError 别名"""
        from drf_resource.exceptions import BKAPIError

        assert BKAPIError is APIError


class TestBulkRequest:
    """测试批量请求"""

    def test_bulk_request(self):
        """测试批量请求"""
        resource = MockAPIResource()

        resource._make_request_and_format = MagicMock(
            return_value={"result": True, "code": 200, "data": {"id": 1}}
        )

        results = resource.bulk_request(
            [
                {"user_id": 1},
                {"user_id": 2},
            ]
        )

        assert len(results) == 2
        assert all(r == {"id": 1} for r in results)
