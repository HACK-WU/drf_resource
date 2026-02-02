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

# 第一步：清除环境变量，避免 .env 文件干扰
os.environ.pop("DJANGO_SETTINGS_MODULE", None)
os.environ.pop("DJANGO_CONF_MODULE", None)

# 第二步：在任何其他导入之前配置 Django
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "rest_framework",
            # 注意：不加载 drf_resource app，避免触发 ResourceFinder
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        REST_FRAMEWORK={
            "TEST_REQUEST_DEFAULT_FORMAT": "json",
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        },
        # drf_resource 需要的配置
        BASE_DIR=os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ),
        API_DIR="api",
        PLATFORM="community",
        ROLE="web",
        APP_CODE="test_app",
        ROOT_URLCONF="tests.api_explorer.urls",  # 测试用 URL 配置
        DRF_RESOURCE={
            "API_EXPLORER_ENABLED": True,
        },
    )
    django.setup()

# 第三步：现在可以安全导入 pytest 和其他模块
import pytest

from rest_framework.serializers import CharField, Serializer
from rest_framework.test import APIClient

# 延迟导入 drf_resource，在 fixture 中按需导入


class MockRequestSerializer(Serializer):
    """Mock 请求序列化器"""

    name = CharField(required=True, max_length=100)
    value = CharField(required=False, default="default_value")


class MockResponseSerializer(Serializer):
    """Mock 响应序列化器"""

    result = CharField()
    data = CharField()


def create_mock_resource_class():
    """创建 Mock Resource 类"""
    from drf_resource.base import Resource

    class MockResource(Resource):
        """Mock Resource 类"""

        RequestSerializer = MockRequestSerializer
        ResponseSerializer = MockResponseSerializer

        method = "POST"
        base_url = "http://mock.example.com"
        action = "/test/action"
        label = "Mock Resource for Testing"

        def perform_request(self, validated_request_data):
            return {
                "result": "success",
                "data": f"Processed: {validated_request_data.get('name', '')}",
            }

    return MockResource


def create_mock_fail_resource_class():
    """创建 Mock 失败的 Resource 类"""
    from drf_resource.base import Resource

    class MockFailResource(Resource):
        """Mock 失败的 Resource"""

        def perform_request(self, validated_request_data):
            raise Exception("Mock Error")

    return MockFailResource


def create_mock_api_shortcut_class():
    """创建 Mock APIResourceShortcut 类"""

    class MockAPIResourceShortcut:
        """Mock APIResourceShortcut，绕过单例模式"""

        _entry = "default"
        _package_pool = {}

        def __init__(self, module_path: str, methods: dict = None):
            self._path = module_path
            self._package = None
            self._methods = methods or {}
            self.loaded = True

        def __getattr__(self, item):
            if item in self._methods:
                return self._methods[item]()
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{item}'"
            )

        def list_method(self):
            return list(self._methods.keys())

    return MockAPIResourceShortcut


@pytest.fixture
def api_client():
    """API 客户端 fixture"""
    return APIClient()


@pytest.fixture
def mock_resource_class():
    """Mock Resource 类 fixture"""
    return create_mock_resource_class()


@pytest.fixture
def mock_fail_resource_class():
    """Mock 失败的 Resource 类 fixture"""
    return create_mock_fail_resource_class()


@pytest.fixture
def mock_api_module(monkeypatch):
    """Mock API 模块 fixture"""
    MockAPIResourceShortcut = create_mock_api_shortcut_class()
    MockResource = create_mock_resource_class()
    MockFailResource = create_mock_fail_resource_class()

    # 创建 mock 模块
    mock_module = MockAPIResourceShortcut(
        "api.mock_module",
        methods={"test_api": MockResource, "fail_api": MockFailResource},
    )

    # 使用 monkeypatch 直接设置 api 对象的属性
    from drf_resource.management import root

    # 直接在 api 对象上设置 mock_module 属性
    monkeypatch.setattr(root.api, "mock_module", mock_module, raising=False)

    return mock_module


@pytest.fixture
def mock_settings_api_explorer_enabled(monkeypatch):
    """Mock settings.DRF_RESOURCE['API_EXPLORER_ENABLED'] = True"""
    try:
        from django.conf import settings

        if not hasattr(settings, "DRF_RESOURCE"):
            monkeypatch.setattr(settings, "DRF_RESOURCE", {})

        settings.DRF_RESOURCE["API_EXPLORER_ENABLED"] = True
        yield
        # 清理
        if (
            hasattr(settings, "DRF_RESOURCE")
            and "API_EXPLORER_ENABLED" in settings.DRF_RESOURCE
        ):
            del settings.DRF_RESOURCE["API_EXPLORER_ENABLED"]
    except ImportError:
        # Django未安装时跳过
        yield


@pytest.fixture
def mock_settings_api_explorer_disabled(monkeypatch):
    """Mock settings.DRF_RESOURCE['API_EXPLORER_ENABLED'] = False"""
    try:
        from django.conf import settings

        if not hasattr(settings, "DRF_RESOURCE"):
            monkeypatch.setattr(settings, "DRF_RESOURCE", {})

        settings.DRF_RESOURCE["API_EXPLORER_ENABLED"] = False
        yield
        # 清理
        if (
            hasattr(settings, "DRF_RESOURCE")
            and "API_EXPLORER_ENABLED" in settings.DRF_RESOURCE
        ):
            del settings.DRF_RESOURCE["API_EXPLORER_ENABLED"]
    except ImportError:
        # Django未安装时跳过
        yield


@pytest.fixture
def mock_debug_mode(monkeypatch):
    """Mock DEBUG=True"""
    try:
        from django.conf import settings

        monkeypatch.setattr(settings, "DEBUG", True)
    except ImportError:
        pass
    yield


@pytest.fixture
def mock_production_mode(monkeypatch):
    """Mock 生产环境（DEBUG=False，无 DRF_RESOURCE 配置）"""
    try:
        from django.conf import settings

        monkeypatch.setattr(settings, "DEBUG", False)

        # 确保没有显式配置
        if hasattr(settings, "DRF_RESOURCE"):
            if "API_EXPLORER_ENABLED" in settings.DRF_RESOURCE:
                del settings.DRF_RESOURCE["API_EXPLORER_ENABLED"]
    except ImportError:
        pass
    yield


@pytest.fixture
def mock_env_dev(monkeypatch):
    """Mock ENV=dev"""
    monkeypatch.setenv("ENV", "dev")
    yield


@pytest.fixture
def mock_env_production(monkeypatch):
    """Mock ENV=production"""
    monkeypatch.setenv("ENV", "production")
    yield
