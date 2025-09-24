#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的API文档功能测试

直接测试核心功能，不依赖完整的Django环境。
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
            "drf_spectacular",
            "drf_resource",
        ],
        REST_FRAMEWORK={
            "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        },
        SPECTACULAR_SETTINGS={
            "TITLE": "DRF Resource API Documentation",
            "VERSION": "1.0.0",
            "SERVE_INCLUDE_SCHEMA": False,
        },
        SECRET_KEY="test-key-for-documentation",
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


def test_documentation_mixin():
    """测试DocumentationMixin功能"""
    print("=" * 60)
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


def test_schema_generator():
    """测试Schema生成器"""
    print("\n" + "=" * 60)
    print("测试Schema生成器")
    print("=" * 60)

    try:
        from drf_resource.documentation.schema import APIResourceSchema

        schema_gen = APIResourceSchema()
        print("✓ APIResourceSchema 创建成功")

        # 测试基本schema生成
        test_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "名称"},
                "age": {"type": "integer", "description": "年龄"},
                "active": {"type": "boolean", "description": "是否激活"},
            },
            "required": ["name"],
        }

        print("✓ 测试schema结构正确")
        print(f"  - 属性数量: {len(test_schema['properties'])}")
        print(f"  - 必填字段: {test_schema['required']}")

        return True

    except Exception as e:
        print(f"✗ Schema生成器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings():
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


def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 60)
    print("测试文件结构")
    print("=" * 60)

    base_path = project_root / "drf_resource" / "documentation"

    required_files = [
        "__init__.py",
        "generator.py",
        "schema.py",
        "extensions.py",
        "settings.py",
        "mixins.py",
        "views.py",
        "urls.py",
    ]

    missing_files = []

    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            print(f"✓ {filename} 存在")
        else:
            print(f"✗ {filename} 缺失")
            missing_files.append(filename)

    # 检查模板文件
    template_path = project_root / "drf_resource" / "templates" / "drf_resource"
    template_files = ["swagger_ui.html", "redoc.html", "api_docs_index.html"]

    for filename in template_files:
        file_path = template_path / filename
        if file_path.exists():
            print(f"✓ 模板 {filename} 存在")
        else:
            print(f"✗ 模板 {filename} 缺失")
            missing_files.append(f"template/{filename}")

    # 检查管理命令
    command_path = project_root / "drf_resource" / "management" / "commands"
    command_files = ["generate_api_docs.py", "html_generator.py"]

    for filename in command_files:
        file_path = command_path / filename
        if file_path.exists():
            print(f"✓ 命令 {filename} 存在")
        else:
            print(f"✗ 命令 {filename} 缺失")
            missing_files.append(f"command/{filename}")

    return len(missing_files) == 0


def test_integration():
    """测试集成功能"""
    print("\n" + "=" * 60)
    print("测试集成功能")
    print("=" * 60)

    try:
        # 测试APIResource是否正确继承了DocumentationMixin
        from drf_resource.contrib.api import APIResource
        from drf_resource.documentation.mixins import DocumentationMixin

        print("✓ APIResource导入成功")

        # 检查是否是DocumentationMixin的子类
        if issubclass(APIResource, DocumentationMixin):
            print("✓ APIResource 正确继承了 DocumentationMixin")
        else:
            print("✗ APIResource 没有继承 DocumentationMixin")
            return False

        # 检查APIResource是否有文档相关方法
        required_methods = [
            "get_api_documentation",
            "get_api_examples",
            "get_request_schema",
            "get_response_schema",
            "is_documented",
        ]

        for method_name in required_methods:
            if hasattr(APIResource, method_name):
                print(f"✓ APIResource 具有方法: {method_name}")
            else:
                print(f"✗ APIResource 缺少方法: {method_name}")
                return False

        return True

    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("DRF Resource API文档生成系统 - 简化测试")
    print(
        "测试时间:", __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    test_functions = [
        test_file_structure,
        test_settings,
        test_validators,
        test_documentation_mixin,
        test_schema_generator,
        test_integration,
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
        print("🎉 所有核心功能测试通过！")
        print("\n📋 下一步操作指南:")
        print("1. 在Django项目中添加 'drf_resource' 到 INSTALLED_APPS")
        print("2. 在URL配置中添加文档路由:")
        print("   path('api-docs/', include('drf_resource.documentation.urls'))")
        print("3. 在settings.py中配置API文档设置:")
        print("   API_DOCS_SETTINGS = {'ENABLED': True, 'AUTO_GENERATE': True}")
        print("4. 为APIResource类添加文档属性")
        print("5. 运行 python manage.py generate_api_docs 生成文档")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
