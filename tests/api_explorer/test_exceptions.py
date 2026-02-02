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

from drf_resource.api_explorer.exceptions import (
    APIExplorerException,
    EnvironmentDeniedError,
    InvocationError,
    ResourceNotFoundError,
)


class TestAPIExplorerException:
    """测试 APIExplorerException 基类"""

    def test_exception_with_message(self):
        """测试创建异常时传入消息"""
        exc = APIExplorerException("Test message")
        assert str(exc) == "Test message"
        assert exc.message == "Test message"
        assert exc.code is None

    def test_exception_with_code(self):
        """测试创建异常时传入错误码"""
        exc = APIExplorerException("Test message", code="500")
        assert exc.message == "Test message"
        assert exc.code == "500"

    def test_exception_can_be_raised(self):
        """测试异常可以被抛出和捕获"""
        with pytest.raises(APIExplorerException) as exc_info:
            raise APIExplorerException("Test error")
        assert "Test error" in str(exc_info.value)


class TestResourceNotFoundError:
    """测试 ResourceNotFoundError 异常"""

    def test_exception_initialization(self):
        """测试异常初始化"""
        exc = ResourceNotFoundError("Resource not found")
        assert str(exc) == "Resource not found"
        assert exc.message == "Resource not found"
        assert exc.code == "404"

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        exc = ResourceNotFoundError("Test")
        assert isinstance(exc, APIExplorerException)
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised(self):
        """测试异常可以被抛出和捕获"""
        with pytest.raises(ResourceNotFoundError) as exc_info:
            raise ResourceNotFoundError("API not found")
        assert "API not found" in str(exc_info.value)
        assert exc_info.value.code == "404"


class TestInvocationError:
    """测试 InvocationError 异常"""

    def test_exception_initialization(self):
        """测试异常初始化"""
        exc = InvocationError("Invocation failed")
        assert str(exc) == "Invocation failed"
        assert exc.message == "Invocation failed"
        assert exc.code == "500"

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        exc = InvocationError("Test")
        assert isinstance(exc, APIExplorerException)
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised(self):
        """测试异常可以被抛出和捕获"""
        with pytest.raises(InvocationError) as exc_info:
            raise InvocationError("API call failed")
        assert "API call failed" in str(exc_info.value)
        assert exc_info.value.code == "500"


class TestEnvironmentDeniedError:
    """测试 EnvironmentDeniedError 异常"""

    def test_exception_with_default_message(self):
        """测试使用默认消息"""
        exc = EnvironmentDeniedError()
        assert "API Explorer 仅在开发/测试环境可用" in str(exc)
        assert exc.code == "403"

    def test_exception_with_custom_message(self):
        """测试使用自定义消息"""
        exc = EnvironmentDeniedError("Custom message")
        assert str(exc) == "Custom message"
        assert exc.code == "403"

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        exc = EnvironmentDeniedError()
        assert isinstance(exc, APIExplorerException)
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised(self):
        """测试异常可以被抛出和捕获"""
        with pytest.raises(EnvironmentDeniedError) as exc_info:
            raise EnvironmentDeniedError()
        assert exc_info.value.code == "403"
