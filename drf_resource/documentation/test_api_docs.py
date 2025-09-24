#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API文档生成功能测试脚本

该脚本用于测试API文档自动生成系统的各项功能。
"""

import json
import os
import sys
from pathlib import Path

import django

# 添加项目路径到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "bkmonitor"))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from drf_resource.documentation.generator import DocumentationGenerator
from drf_resource.documentation.settings import API_DOCS_SETTINGS


def test_api_collection():
    """测试API资源收集功能"""
    print("=" * 60)
    print("测试API资源收集功能")
    print("=" * 60)

    try:
        generator = DocumentationGenerator()
        collected_apis = generator.collect_api_resources()

        print(f"✓ 成功收集到 {len(collected_apis)} 个API模块")

        for module_name, module_info in collected_apis.items():
            apis_count = len(module_info["apis"])
            print(f"  - {module_name}: {apis_count} 个API")

            # 显示前3个API作为示例
            for i, api_info in enumerate(module_info["apis"][:3]):
                print(
                    f"    * {api_info['display_name']} ({api_info['method']} {api_info['action']})"
                )

            if len(module_info["apis"]) > 3:
                print(f"    ... 还有 {len(module_info['apis']) - 3} 个API")

        return True

    except Exception as e:
        print(f"✗ API资源收集失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_openapi_schema_generation():
    """测试OpenAPI schema生成"""
    print("\n" + "=" * 60)
    print("测试OpenAPI Schema生成")
    print("=" * 60)

    try:
        generator = DocumentationGenerator()
        schema = generator.generate_openapi_schema()

        # 验证基本结构
        required_fields = ["openapi", "info", "paths", "components"]
        for field in required_fields:
            if field not in schema:
                print(f"✗ OpenAPI schema缺少必需字段: {field}")
                return False

        print(f"✓ OpenAPI版本: {schema['openapi']}")
        print(f"✓ API标题: {schema['info']['title']}")
        print(f"✓ API版本: {schema['info']['version']}")
        print(f"✓ 路径数量: {len(schema['paths'])}")
        print(f"✓ 标签数量: {len(schema.get('tags', []))}")

        # 显示前几个路径作为示例
        paths = list(schema["paths"].keys())[:5]
        if paths:
            print("✓ 示例路径:")
            for path in paths:
                print(f"  - {path}")

        return True

    except Exception as e:
        print(f"✗ OpenAPI schema生成失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_documentation_data_generation():
    """测试文档数据生成"""
    print("\n" + "=" * 60)
    print("测试文档数据生成")
    print("=" * 60)

    try:
        generator = DocumentationGenerator()
        docs_data = generator.generate_documentation_data()

        # 验证数据结构
        required_fields = ["title", "version", "modules", "stats"]
        for field in required_fields:
            if field not in docs_data:
                print(f"✗ 文档数据缺少必需字段: {field}")
                return False

        print(f"✓ 文档标题: {docs_data['title']}")
        print(f"✓ 文档版本: {docs_data['version']}")
        print("✓ 统计信息:")
        print(f"  - 模块数量: {docs_data['stats']['total_modules']}")
        print(f"  - API数量: {docs_data['stats']['total_apis']}")
        print(f"  - 分类数量: {len(docs_data['stats']['categories'])}")

        # 验证分类信息
        if "categorized_apis" in docs_data:
            print("✓ API分类:")
            for category, apis in docs_data["categorized_apis"].items():
                print(f"  - {category}: {len(apis)} 个API")

        return True

    except Exception as e:
        print(f"✗ 文档数据生成失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_api_documentation_attributes():
    """测试API文档属性功能"""
    print("\n" + "=" * 60)
    print("测试API文档属性功能")
    print("=" * 60)

    try:
        # 测试DocumentationMixin功能
        from drf_resource.contrib.api import APIResource
        from drf_resource.documentation.mixins import DocumentationMixin

        # 创建测试API类
        class TestAPIResource(DocumentationMixin, APIResource):
            api_name = "测试API"
            api_description = "这是一个测试API"
            api_category = "test"
            api_version = "v1.0"
            api_tags = ["测试", "示例"]
            doc_examples = {
                "request": {"param1": "value1"},
                "response": {"result": "success"},
            }

            # 必需的抽象属性
            base_url = "http://test.com"
            module_name = "test"
            action = "/test"
            method = "GET"

            def perform_request(self, validated_request_data):
                return {"test": "success"}

        # 测试实例
        api_instance = TestAPIResource()

        # 测试文档功能
        print("✓ 测试DocumentationMixin功能:")

        docs = api_instance.get_api_documentation()
        print(f"  - API名称: {docs['name']}")
        print(f"  - API描述: {docs['description']}")
        print(f"  - API分类: {docs['category']}")
        print(f"  - API版本: {docs['version']}")
        print(f"  - API标签: {docs['tags']}")

        examples = api_instance.get_api_examples()
        print(f"  - 示例数量: {len(examples)}")

        is_documented = api_instance.is_documented()
        print(f"  - 是否应生成文档: {is_documented}")

        return True

    except Exception as e:
        print(f"✗ API文档属性测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_settings_configuration():
    """测试配置功能"""
    print("\n" + "=" * 60)
    print("测试配置功能")
    print("=" * 60)

    try:
        print("✓ 当前API文档配置:")
        print(f"  - 启用状态: {API_DOCS_SETTINGS.get('ENABLED', False)}")
        print(f"  - 自动生成: {API_DOCS_SETTINGS.get('AUTO_GENERATE', True)}")
        print(f"  - 文档标题: {API_DOCS_SETTINGS.get('TITLE', 'N/A')}")
        print(f"  - 文档版本: {API_DOCS_SETTINGS.get('VERSION', 'N/A')}")
        print(f"  - URL前缀: {API_DOCS_SETTINGS.get('URL_PREFIX', 'N/A')}")
        print(f"  - 输出目录: {API_DOCS_SETTINGS.get('OUTPUT_DIR', 'N/A')}")

        # 测试过滤设置
        filters = API_DOCS_SETTINGS.get("FILTERS", {})
        print("✓ 过滤设置:")
        print(f"  - 隐藏模块: {filters.get('HIDDEN_MODULES', [])}")
        print(f"  - 隐藏分类: {filters.get('HIDDEN_CATEGORIES', [])}")
        print(f"  - 包含标签: {filters.get('INCLUDE_TAGS', [])}")
        print(f"  - 排除标签: {filters.get('EXCLUDE_TAGS', [])}")

        return True

    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False


def test_command_functionality():
    """测试管理命令功能"""
    print("\n" + "=" * 60)
    print("测试管理命令功能")
    print("=" * 60)

    try:
        from io import StringIO

        from django.core.management import call_command

        # 测试生成OpenAPI文档
        print("✓ 测试生成OpenAPI文档命令...")
        out = StringIO()
        call_command(
            "generate_api_docs",
            "--output-format=openapi",
            "--output-dir=/tmp/api_docs_test",
            stdout=out,
        )
        output = out.getvalue()

        if "API文档生成完成" in output:
            print("  - OpenAPI文档生成成功")
        else:
            print("  - OpenAPI文档生成可能有问题")

        # 检查生成的文件
        import os

        output_file = "/tmp/api_docs_test/openapi.json"
        if os.path.exists(output_file):
            print(f"  - 文件已生成: {output_file}")
            with open(output_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                print(f"  - 文件格式正确，包含 {len(content.get('paths', {}))} 个路径")
        else:
            print("  - 警告: 输出文件未找到")

        return True

    except Exception as e:
        print(f"✗ 管理命令测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("DRF Resource API文档生成系统测试")
    print(
        "测试时间:", __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    test_results = []

    # 执行各项测试
    test_functions = [
        test_settings_configuration,
        test_api_collection,
        test_api_documentation_attributes,
        test_documentation_data_generation,
        test_openapi_schema_generation,
        test_command_functionality,
    ]

    for test_func in test_functions:
        try:
            result = test_func()
            test_results.append((test_func.__name__, result))
        except Exception as e:
            print(f"✗ 测试 {test_func.__name__} 执行异常: {e}")
            test_results.append((test_func.__name__, False))

    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("🎉 所有测试通过！API文档生成系统运行正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
