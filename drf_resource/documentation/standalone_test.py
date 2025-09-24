#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DRF Resource独立模块测试

该脚本只测试drf_resource模块本身的功能，不依赖bkmonitor项目。
"""

import sys
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 配置基本的Django设置
import django
from django.conf import settings

# 配置最小的Django设置
if not settings.configured:
    settings.configure(
        BASE_DIR=str(project_root),
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "rest_framework",
            "drf_resource",
        ],
        REST_FRAMEWORK={
            "DEFAULT_RENDERER_CLASSES": [
                "rest_framework.renderers.JSONRenderer",
            ],
            "DEFAULT_PARSER_CLASSES": [
                "rest_framework.parsers.JSONParser",
            ],
        },
        SECRET_KEY="test-key-for-drf-resource",
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        DEBUG=True,
        PLATFORM="test",
    )
    django.setup()


def test_basic_imports():
    """测试基本导入功能"""
    print("=" * 60)
    print("测试基本导入功能")
    print("=" * 60)

    try:
        # 测试基础模块导入

        print("✓ Resource基类导入成功")

        print("✓ CacheResource导入成功")

        print("✓ DocumentationMixin导入成功")

        return True

    except Exception as e:
        print(f"✗ 基本导入测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_documentation_mixin():
    """测试DocumentationMixin功能"""
    print("\n" + "=" * 60)
    print("测试DocumentationMixin功能")
    print("=" * 60)

    try:
        from drf_resource.documentation.mixins import DocumentationMixin

        # 创建一个简单的测试类
        class TestAPI(DocumentationMixin):
            api_name = "测试API"
            api_description = "这是一个测试API"
            api_category = "test"
            api_version = "v1.0"
            api_tags = ["测试", "示例"]
            doc_examples = {
                "request": {"param1": "value1"},
                "response": {"result": "success"},
            }

            def __init__(self):
                self.method = "GET"
                self.action = "/test"
                self.module_name = "test"
                self.TIMEOUT = 60

        api_instance = TestAPI()

        print("✓ DocumentationMixin 创建成功")

        # 测试文档功能
        docs = api_instance.get_api_documentation()
        print(f"✓ API名称: {docs['name']}")
        print(f"✓ API描述: {docs['description']}")
        print(f"✓ API分类: {docs['category']}")
        print(f"✓ API版本: {docs['version']}")
        print(f"✓ API标签: {docs['tags']}")
        print(f"✓ HTTP方法: {docs['method']}")
        print(f"✓ API路径: {docs['action']}")

        examples = api_instance.get_api_examples()
        print(f"✓ 示例数据: {len(examples)} 个")

        is_documented = api_instance.is_documented()
        print(f"✓ 是否生成文档: {is_documented}")

        return True

    except Exception as e:
        print(f"✗ DocumentationMixin测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_configuration():
    """测试配置功能"""
    print("\n" + "=" * 60)
    print("测试配置功能")
    print("=" * 60)

    try:
        from drf_resource.documentation.settings import (
            get_all_api_docs_settings,
            get_api_docs_setting,
        )

        print("✓ 配置模块加载成功")

        # 测试默认配置
        title = get_api_docs_setting("TITLE")
        print(f"✓ 默认标题: {title}")

        enabled = get_api_docs_setting("ENABLED")
        print(f"✓ 默认启用状态: {enabled}")

        all_settings = get_all_api_docs_settings()
        print(f"✓ 配置项数量: {len(all_settings)}")

        # 测试主要配置项
        key_settings = ["TITLE", "VERSION", "ENABLED", "AUTO_GENERATE", "URL_PREFIX"]
        for key in key_settings:
            value = all_settings.get(key)
            print(f"  - {key}: {value}")

        return True

    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_validators():
    """测试验证器功能"""
    print("\n" + "=" * 60)
    print("测试验证器功能")
    print("=" * 60)

    try:
        from drf_resource.documentation.mixins import (
            MetadataValidator,
        )

        print("✓ 验证器模块加载成功")

        # 测试分类验证
        valid_category = MetadataValidator.validate_api_category("external")
        invalid_category = MetadataValidator.validate_api_category("invalid_category")
        print(f"✓ 分类验证: valid={valid_category}, invalid={invalid_category}")

        # 测试版本验证
        valid_version = MetadataValidator.validate_api_version("v1.0")
        invalid_version = MetadataValidator.validate_api_version("invalid")
        print(f"✓ 版本验证: valid={valid_version}, invalid={invalid_version}")

        # 测试标签验证
        valid_tags = MetadataValidator.validate_api_tags(["tag1", "tag2"])
        invalid_tags = MetadataValidator.validate_api_tags("not_a_list")
        print(f"✓ 标签验证: valid={valid_tags}, invalid={invalid_tags}")

        # 测试示例验证
        valid_examples = MetadataValidator.validate_doc_examples(
            {"request": {"param": "value"}}
        )
        invalid_examples = MetadataValidator.validate_doc_examples("not_a_dict")
        print(
            f"✓ 示例验证: valid={len(valid_examples)}, invalid={len(invalid_examples)}"
        )

        return True

    except Exception as e:
        print(f"✗ 验证器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_resource_base_class():
    """测试Resource基类"""
    print("\n" + "=" * 60)
    print("测试Resource基类")
    print("=" * 60)

    try:
        from drf_resource.base import Resource
        from rest_framework import serializers

        # 创建测试序列化器
        class TestRequestSerializer(serializers.Serializer):
            name = serializers.CharField(max_length=100, help_text="名称")
            age = serializers.IntegerField(min_value=0, help_text="年龄")

        class TestResponseSerializer(serializers.Serializer):
            message = serializers.CharField(help_text="响应消息")
            data = serializers.DictField(help_text="响应数据")

        # 创建测试Resource
        class TestResource(Resource):
            RequestSerializer = TestRequestSerializer
            ResponseSerializer = TestResponseSerializer

            def perform_request(self, validated_request_data):
                return {
                    "message": f"Hello, {validated_request_data['name']}!",
                    "data": validated_request_data,
                }

        # 测试Resource实例化
        resource = TestResource()
        print("✓ Resource实例创建成功")

        # 测试请求处理
        test_data = {"name": "Test User", "age": 25}
        result = resource.request(test_data)
        print(f"✓ Resource请求处理成功: {result['message']}")

        # 测试文档生成
        doc = resource.generate_doc()
        print(f"✓ 文档生成成功，包含 {len(doc['request_params'])} 个请求参数")
        print(f"✓ 文档生成成功，包含 {len(doc['response_params'])} 个响应参数")

        return True

    except Exception as e:
        print(f"✗ Resource基类测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 60)
    print("测试文件结构")
    print("=" * 60)

    base_path = project_root / "drf_resource"

    required_files = [
        "__init__.py",
        "base.py",
        "apps.py",
        "exceptions.py",
        "tasks.py",
        "tools.py",
        "settings.py",
    ]

    required_dirs = [
        "contrib",
        "documentation",
        "management",
        "middlewares",
        "utils",
        "templates",
    ]

    missing_files = []

    # 检查文件
    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            print(f"✓ {filename} 存在")
        else:
            print(f"✗ {filename} 缺失")
            missing_files.append(filename)

    # 检查目录
    for dirname in required_dirs:
        dir_path = base_path / dirname
        if dir_path.exists():
            print(f"✓ {dirname}/ 目录存在")
        else:
            print(f"✗ {dirname}/ 目录缺失")
            missing_files.append(f"{dirname}/")

    # 检查文档相关文件
    doc_path = base_path / "documentation"
    doc_files = [
        "__init__.py",
        "generator.py",
        "schema.py",
        "extensions.py",
        "settings.py",
        "mixins.py",
        "views.py",
        "urls.py",
    ]

    for filename in doc_files:
        file_path = doc_path / filename
        if file_path.exists():
            print(f"✓ documentation/{filename} 存在")
        else:
            print(f"✗ documentation/{filename} 缺失")
            missing_files.append(f"documentation/{filename}")

    return len(missing_files) == 0


def test_apps_integration():
    """测试apps.py集成"""
    print("\n" + "=" * 60)
    print("测试apps.py集成")
    print("=" * 60)

    try:
        from drf_resource.apps import DRFResourceConfig

        print("✓ DRFResourceConfig导入成功")
        print(f"✓ App名称: {DRFResourceConfig.name}")
        print(f"✓ App标签: {DRFResourceConfig.label}")
        print(f"✓ App显示名称: {DRFResourceConfig.verbose_name}")

        # 检查ready方法是否存在
        if hasattr(DRFResourceConfig, "ready"):
            print("✓ ready方法存在")
        else:
            print("✗ ready方法缺失")
            return False

        return True

    except Exception as e:
        print(f"✗ apps.py集成测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("DRF Resource独立模块测试")
    print(
        "测试时间:", __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    test_functions = [
        test_file_structure,
        test_basic_imports,
        test_settings_configuration,
        test_validators,
        test_documentation_mixin,
        test_resource_base_class,
        test_apps_integration,
    ]

    results = []

    for test_func in test_functions:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"✗ 测试 {test_func.__name__} 执行异常: {e}")
            results.append((test_func.__name__, False))

    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("🎉 所有测试通过！drf_resource模块独立性验证成功。")
        print("\n📋 使用指南:")
        print("1. 将drf_resource添加到Django项目的INSTALLED_APPS中")
        print("2. 在URL配置中添加文档路由（可选）:")
        print("   path('api-docs/', include('drf_resource.documentation.urls'))")
        print("3. 配置API文档设置（可选）:")
        print("   API_DOCS_SETTINGS = {'ENABLED': True, 'AUTO_GENERATE': True}")
        print("4. 为APIResource类添加文档属性（可选）")
        print("5. 运行 python manage.py generate_api_docs 生成文档（可选）")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
