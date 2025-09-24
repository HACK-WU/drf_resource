# -*- coding: utf-8 -*-
"""
DRF Spectacular扩展

该模块为drf-spectacular提供自定义扩展，以支持APIResource类的文档生成。
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from drf_spectacular.extensions import OpenApiSchemaExtension
except ImportError:
    # 如果导入失败，创建一个空的基类
    class OpenApiSchemaExtension:
        target_component = None
        priority = 1

        def map_serializer(self, auto_schema, direction):
            return {}


try:
    from drf_spectacular.openapi import AutoSchema
except ImportError:

    class AutoSchema:
        def __init__(self):
            pass

        def get_operation_id(self, path, method):
            return f"{method.lower()}_{path.replace('/', '_')}"

        def get_tags(self, operation):
            return []


try:
    from drf_spectacular.utils import extend_schema
except ImportError:

    def extend_schema(**kwargs):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)


class APIResourceExtension(OpenApiSchemaExtension):
    """
    APIResource的drf-spectacular扩展

    为APIResource类提供OpenAPI schema生成支持。
    """

    target_component = "drf_resource.contrib.api.APIResource"
    priority = 1

    def map_serializer(self, auto_schema: AutoSchema, direction: str) -> Dict[str, Any]:
        """
        映射序列化器到OpenAPI schema

        Args:
            auto_schema: AutoSchema实例
            direction: 'request' 或 'response'

        Returns:
            Dict: OpenAPI格式的schema
        """
        try:
            # 获取APIResource实例
            resource_instance = getattr(auto_schema.view, "resource", None)
            if not resource_instance:
                return {}

            resource_class = resource_instance.__class__

            # 根据方向选择对应的序列化器
            if direction == "request":
                serializer_class = getattr(resource_class, "RequestSerializer", None)
            else:
                serializer_class = getattr(resource_class, "ResponseSerializer", None)

            if not serializer_class:
                return {}

            # 使用标准的序列化器映射
            serializer_instance = serializer_class()
            return auto_schema._map_serializer(serializer_instance, direction)

        except Exception as e:
            logger.warning(f"APIResource扩展映射失败: {e}")
            return {}

    def get_operation_id(self, auto_schema: AutoSchema, path: str, method: str) -> str:
        """
        生成操作ID

        Args:
            auto_schema: AutoSchema实例
            path: API路径
            method: HTTP方法

        Returns:
            str: 操作ID
        """
        try:
            resource_instance = getattr(auto_schema.view, "resource", None)
            if resource_instance:
                resource_class = resource_instance.__class__
                module_name = getattr(resource_class, "module_name", "unknown")
                class_name = resource_class.__name__.replace("Resource", "")
                return f"{module_name}_{class_name}_{method.lower()}"
        except:
            pass

        return auto_schema.get_operation_id(path, method)

    def get_tags(self, auto_schema: AutoSchema, operation: Dict[str, Any]) -> List[str]:
        """
        生成标签

        Args:
            auto_schema: AutoSchema实例
            operation: 操作信息

        Returns:
            List[str]: 标签列表
        """
        try:
            resource_instance = getattr(auto_schema.view, "resource", None)
            if resource_instance:
                resource_class = resource_instance.__class__

                tags = []

                # 添加模块标签
                module_name = getattr(resource_class, "module_name", None)
                if module_name:
                    tags.append(module_name)

                # 添加自定义标签
                api_tags = getattr(resource_class, "api_tags", [])
                tags.extend(api_tags)

                # 添加分类标签
                category = getattr(resource_class, "api_category", None)
                if category:
                    tags.append(category)

                return tags
        except:
            pass

        return auto_schema.get_tags(operation)


class APIResourceAutoSchema(AutoSchema):
    """
    为APIResource定制的AutoSchema

    提供更好的APIResource支持和文档生成。
    """

    def get_operation(self, path: str, method: str) -> Dict[str, Any]:
        """
        获取操作信息

        Args:
            path: API路径
            method: HTTP方法

        Returns:
            Dict: 操作信息
        """
        operation = super().get_operation(path, method)

        try:
            # 尝试从resource获取额外信息
            resource_instance = getattr(self.view, "resource", None)
            if resource_instance:
                resource_class = resource_instance.__class__

                # 添加自定义描述
                api_description = getattr(resource_class, "api_description", None)
                if api_description:
                    operation["description"] = api_description

                # 添加自定义摘要
                api_name = getattr(resource_class, "api_name", None)
                if api_name:
                    operation["summary"] = api_name

                # 标记废弃状态
                deprecated = getattr(resource_class, "deprecated", False)
                if deprecated:
                    operation["deprecated"] = True
                    deprecation_message = getattr(
                        resource_class, "deprecation_message", None
                    )
                    if deprecation_message:
                        description = operation.get("description", "")
                        operation["description"] = (
                            f"{description}\n\n**Deprecated**: {deprecation_message}"
                        )

                # 添加示例
                examples = getattr(resource_class, "doc_examples", {})
                if examples and "request" in examples:
                    self._add_request_example(operation, examples["request"])

        except Exception as e:
            logger.warning(f"获取操作信息时出错: {e}")

        return operation

    def _add_request_example(self, operation: Dict[str, Any], example: Any):
        """添加请求示例"""
        try:
            if "requestBody" in operation:
                content = operation["requestBody"].get("content", {})
                for media_type in content:
                    if "examples" not in content[media_type]:
                        content[media_type]["examples"] = {}
                    content[media_type]["examples"]["example1"] = {
                        "summary": "Example request",
                        "value": example,
                    }
        except Exception as e:
            logger.warning(f"添加请求示例失败: {e}")

    def get_summary(self) -> Optional[str]:
        """获取摘要"""
        try:
            resource_instance = getattr(self.view, "resource", None)
            if resource_instance:
                resource_class = resource_instance.__class__
                api_name = getattr(resource_class, "api_name", None)
                if api_name:
                    return api_name
        except:
            pass

        return super().get_summary()

    def get_description(self) -> Optional[str]:
        """获取描述"""
        try:
            resource_instance = getattr(self.view, "resource", None)
            if resource_instance:
                resource_class = resource_instance.__class__
                api_description = getattr(resource_class, "api_description", None)
                if api_description:
                    return api_description
        except:
            pass

        return super().get_description()

    def is_deprecated(self) -> bool:
        """检查是否已废弃"""
        try:
            resource_instance = getattr(self.view, "resource", None)
            if resource_instance:
                resource_class = resource_instance.__class__
                return getattr(resource_class, "deprecated", False)
        except:
            pass

        return super().is_deprecated()
