# -*- coding: utf-8 -*-
"""
API文档支持Mixin

该模块为APIResource类提供文档相关功能的Mixin类。
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DocumentationMixin:
    """
    为APIResource类提供文档支持的Mixin

    该Mixin添加了文档相关的属性和方法，同时保持向后兼容性。
    """

    # 文档相关属性
    api_name: Optional[str] = None
    api_description: Optional[str] = None
    api_category: str = "external"
    api_version: str = "v1"
    api_tags: List[str] = []
    doc_examples: Dict[str, Any] = {}
    doc_hidden: bool = False
    rate_limit: Optional[str] = None
    deprecated: bool = False
    deprecation_message: Optional[str] = None

    def get_api_documentation(self) -> Dict[str, Any]:
        """
        获取完整的API文档信息

        Returns:
            Dict: 包含所有文档信息的字典
        """
        return {
            "name": self.api_name or self._get_default_api_name(),
            "description": self.api_description or self._get_default_description(),
            "category": self.api_category,
            "version": self.api_version,
            "tags": self.api_tags.copy() if self.api_tags else [],
            "examples": self.doc_examples.copy() if self.doc_examples else {},
            "hidden": self.doc_hidden,
            "rate_limit": self.rate_limit,
            "deprecated": self.deprecated,
            "deprecation_message": self.deprecation_message,
            "method": getattr(self, "method", "GET").upper(),
            "action": getattr(self, "action", ""),
            "module_name": getattr(self, "module_name", "unknown"),
            "timeout": getattr(self, "TIMEOUT", 60),
            "class_path": f"{self.__class__.__module__}.{self.__class__.__qualname__}",
        }

    def get_api_examples(self) -> Dict[str, Any]:
        """
        获取API使用示例

        Returns:
            Dict: API示例数据
        """
        examples = self.doc_examples.copy() if self.doc_examples else {}

        # 如果没有提供示例，尝试生成默认示例
        if not examples:
            examples = self._generate_default_examples()

        return examples

    def get_request_schema(self) -> Dict[str, Any]:
        """
        获取请求参数结构信息

        Returns:
            Dict: 请求参数schema
        """
        try:
            if hasattr(self, "RequestSerializer") and self.RequestSerializer:
                from ..documentation.schema import APIResourceSchema

                schema_generator = APIResourceSchema()
                return schema_generator.extract_serializer_schema(
                    self.RequestSerializer
                )
        except Exception as e:
            logger.warning(f"获取请求schema失败: {e}")

        return {}

    def get_response_schema(self) -> Dict[str, Any]:
        """
        获取响应参数结构信息

        Returns:
            Dict: 响应参数schema
        """
        try:
            if hasattr(self, "ResponseSerializer") and self.ResponseSerializer:
                from ..documentation.schema import APIResourceSchema

                schema_generator = APIResourceSchema()
                return schema_generator.extract_serializer_schema(
                    self.ResponseSerializer
                )
        except Exception as e:
            logger.warning(f"获取响应schema失败: {e}")

        return {}

    def is_documented(self) -> bool:
        """
        判断是否应该包含在文档中

        Returns:
            bool: 是否应该生成文档
        """
        return not self.doc_hidden

    def _get_default_api_name(self) -> str:
        """获取默认的API名称"""
        class_name = self.__class__.__name__
        if class_name.endswith("Resource"):
            class_name = class_name[:-8]  # 移除 'Resource' 后缀

        # 将驼峰命名转换为更友好的显示名称
        import re

        name = re.sub(r"([A-Z])", r" \1", class_name).strip()
        return name

    def _get_default_description(self) -> str:
        """获取默认的API描述"""
        # 优先使用类的文档字符串
        if self.__class__.__doc__:
            return self.__class__.__doc__.strip()

        # 如果没有文档字符串，生成默认描述
        api_name = self.api_name or self._get_default_api_name()
        return f"{api_name} API"

    def _generate_default_examples(self) -> Dict[str, Any]:
        """生成默认示例"""
        examples = {}

        try:
            # 为请求生成示例
            if hasattr(self, "RequestSerializer") and self.RequestSerializer:
                request_example = self._generate_serializer_example(
                    self.RequestSerializer
                )
                if request_example:
                    examples["request"] = request_example

            # 为响应生成示例
            if hasattr(self, "ResponseSerializer") and self.ResponseSerializer:
                response_example = self._generate_serializer_example(
                    self.ResponseSerializer
                )
                if response_example:
                    examples["response"] = response_example

        except Exception as e:
            logger.warning(f"生成默认示例失败: {e}")

        return examples

    def _generate_serializer_example(
        self, serializer_class
    ) -> Optional[Dict[str, Any]]:
        """从序列化器生成示例数据"""
        try:
            serializer = serializer_class()
            example = {}

            for field_name, field in serializer.fields.items():
                example_value = self._get_field_example_value(field)
                if example_value is not None:
                    example[field_name] = example_value

            return example if example else None

        except Exception as e:
            logger.warning(f"生成序列化器示例失败: {e}")
            return None

    def _get_field_example_value(self, field):
        """获取字段的示例值"""
        from rest_framework import serializers

        # 如果字段有默认值，使用默认值
        if hasattr(field, "default") and field.default != serializers.empty:
            if not callable(field.default):
                return field.default

        # 根据字段类型生成示例值
        if isinstance(field, serializers.CharField):
            return "example_string"
        elif isinstance(field, serializers.IntegerField):
            return 123
        elif isinstance(field, serializers.FloatField):
            return 123.45
        elif isinstance(field, serializers.BooleanField):
            return True
        elif isinstance(field, serializers.DateTimeField):
            return "2024-01-01T12:00:00Z"
        elif isinstance(field, serializers.DateField):
            return "2024-01-01"
        elif isinstance(field, serializers.TimeField):
            return "12:00:00"
        elif isinstance(field, serializers.EmailField):
            return "example@example.com"
        elif isinstance(field, serializers.URLField):
            return "https://example.com"
        elif isinstance(field, serializers.ListField):
            if hasattr(field, "child"):
                child_example = self._get_field_example_value(field.child)
                return [child_example] if child_example is not None else []
            return []
        elif isinstance(field, serializers.DictField):
            return {}
        elif isinstance(field, serializers.JSONField):
            return {}
        else:
            return None


class MetadataValidator:
    """
    验证和标准化文档元数据
    """

    @staticmethod
    def validate_api_category(category: str) -> str:
        """验证API分类"""
        valid_categories = ["external", "internal", "deprecated", "beta"]
        if category not in valid_categories:
            logger.warning(f"无效的API分类: {category}, 使用默认值 'external'")
            return "external"
        return category

    @staticmethod
    def validate_api_version(version: str) -> str:
        """验证API版本"""
        import re

        if not re.match(r"^v?\d+(\.\d+)*$", version):
            logger.warning(f"无效的API版本格式: {version}, 使用默认值 'v1'")
            return "v1"
        return version

    @staticmethod
    def validate_api_tags(tags: List[str]) -> List[str]:
        """验证API标签"""
        if not isinstance(tags, list):
            logger.warning(f"API标签必须是列表: {tags}, 使用空列表")
            return []

        # 过滤空字符串和非字符串类型
        valid_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                valid_tags.append(tag.strip())

        return valid_tags

    @staticmethod
    def validate_doc_examples(examples: Dict[str, Any]) -> Dict[str, Any]:
        """验证文档示例"""
        if not isinstance(examples, dict):
            logger.warning(f"文档示例必须是字典: {examples}, 使用空字典")
            return {}

        return examples


class ExampleValidator:
    """
    验证API示例数据的正确性
    """

    @staticmethod
    def validate_request_example(serializer_class, example_data: Any) -> bool:
        """验证请求示例数据"""
        if not serializer_class or not example_data:
            return True

        try:
            serializer = serializer_class(data=example_data)
            return serializer.is_valid()
        except Exception as e:
            logger.warning(f"请求示例验证失败: {e}")
            return False

    @staticmethod
    def validate_response_example(serializer_class, example_data: Any) -> bool:
        """验证响应示例数据"""
        if not serializer_class or not example_data:
            return True

        try:
            serializer = serializer_class(data=example_data)
            return serializer.is_valid()
        except Exception as e:
            logger.warning(f"响应示例验证失败: {e}")
            return False
