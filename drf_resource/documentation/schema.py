# -*- coding: utf-8 -*-
"""
API资源Schema生成器

该模块负责将APIResource类的元数据转换为OpenAPI格式的schema。
"""

import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from rest_framework import serializers

logger = logging.getLogger(__name__)


class APIResourceSchema:
    """
    APIResource Schema生成器

    负责将APIResource的元数据转换为OpenAPI 3.0格式的schema。
    """

    def __init__(self):
        self.auto_schema = AutoSchema()

    def extract_serializer_schema(self, serializer_class) -> Dict[str, Any]:
        """
        从序列化器类提取schema信息

        Args:
            serializer_class: 序列化器类

        Returns:
            Dict: Schema信息
        """
        if not serializer_class:
            return {}

        try:
            # 创建序列化器实例
            serializer = serializer_class()

            # 提取字段信息
            fields_schema = {}
            required_fields = []

            for field_name, field in serializer.fields.items():
                field_schema = self._extract_field_schema(field_name, field)
                if field_schema:
                    fields_schema[field_name] = field_schema

                # 检查是否为必填字段
                if field.required:
                    required_fields.append(field_name)

            schema = {
                "type": "object",
                "properties": fields_schema,
                "required": required_fields,
            }

            return schema

        except Exception as e:
            logger.warning(f"提取序列化器schema失败: {e}")
            return {}

    def _extract_field_schema(self, field_name: str, field) -> Optional[Dict[str, Any]]:
        """
        提取单个字段的schema信息

        Args:
            field_name: 字段名称
            field: 字段实例

        Returns:
            Dict: 字段schema信息
        """
        try:
            schema = {}

            # 基础类型映射
            field_type_mapping = {
                serializers.CharField: {"type": "string"},
                serializers.IntegerField: {"type": "integer"},
                serializers.FloatField: {"type": "number"},
                serializers.BooleanField: {"type": "boolean"},
                serializers.DateTimeField: {"type": "string", "format": "date-time"},
                serializers.DateField: {"type": "string", "format": "date"},
                serializers.TimeField: {"type": "string", "format": "time"},
                serializers.EmailField: {"type": "string", "format": "email"},
                serializers.URLField: {"type": "string", "format": "uri"},
                serializers.UUIDField: {"type": "string", "format": "uuid"},
                serializers.JSONField: {"type": "object"},
                serializers.DictField: {"type": "object"},
                serializers.ListField: {"type": "array"},
            }

            # 获取基础类型
            field_class = field.__class__
            if field_class in field_type_mapping:
                schema.update(field_type_mapping[field_class])
            else:
                # 检查是否继承自某个基础类型
                for base_class, base_schema in field_type_mapping.items():
                    if isinstance(field, base_class):
                        schema.update(base_schema)
                        break
                else:
                    schema["type"] = "string"  # 默认类型

            # 添加描述信息
            if hasattr(field, "help_text") and field.help_text:
                schema["description"] = str(field.help_text)
            elif hasattr(field, "label") and field.label:
                schema["description"] = str(field.label)

            # 添加默认值
            if hasattr(field, "default") and field.default != serializers.empty:
                if not callable(field.default):
                    schema["default"] = field.default

            # 添加枚举值
            if hasattr(field, "choices") and field.choices:
                schema["enum"] = [choice[0] for choice in field.choices]

            # 添加长度限制
            if hasattr(field, "max_length") and field.max_length:
                schema["maxLength"] = field.max_length
            if hasattr(field, "min_length") and field.min_length:
                schema["minLength"] = field.min_length

            # 添加数值范围
            if hasattr(field, "max_value") and field.max_value is not None:
                schema["maximum"] = field.max_value
            if hasattr(field, "min_value") and field.min_value is not None:
                schema["minimum"] = field.min_value

            # 处理数组类型的子项
            if isinstance(field, serializers.ListField) and hasattr(field, "child"):
                child_schema = self._extract_field_schema(
                    f"{field_name}_item", field.child
                )
                if child_schema:
                    schema["items"] = child_schema

            # 处理嵌套序列化器
            if isinstance(field, serializers.Serializer):
                nested_schema = self.extract_serializer_schema(field.__class__)
                if nested_schema:
                    schema = nested_schema

            return schema

        except Exception as e:
            logger.warning(f"提取字段schema失败 {field_name}: {e}")
            return None

    def generate_openapi_schema(self, collected_apis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成OpenAPI 3.0格式的完整schema

        Args:
            collected_apis: 收集到的API信息

        Returns:
            Dict: OpenAPI格式的schema
        """
        openapi_schema = {
            "openapi": "3.0.3",
            "info": {
                "title": "DRF Resource API Documentation",
                "version": "1.0.0",
                "description": "Auto-generated API documentation for DRF Resource framework",
            },
            "servers": self._get_servers(),
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": self._get_security_schemes(),
            },
            "tags": self._generate_tags(collected_apis),
        }

        # 生成paths
        for module_name, module_info in collected_apis.items():
            for api_info in module_info["apis"]:
                path_info = self._generate_path_info(module_name, api_info)
                if path_info:
                    path, operation = path_info
                    if path not in openapi_schema["paths"]:
                        openapi_schema["paths"][path] = {}
                    openapi_schema["paths"][path][api_info["method"].lower()] = (
                        operation
                    )

        return openapi_schema

    def _get_servers(self) -> List[Dict[str, str]]:
        """获取服务器信息"""
        servers = []

        # 从设置中获取基础URL
        if hasattr(settings, "API_DOCS_BASE_URL"):
            servers.append(
                {"url": settings.API_DOCS_BASE_URL, "description": "Production server"}
            )
        else:
            servers.append(
                {"url": "http://localhost:8000", "description": "Development server"}
            )

        return servers

    def _get_security_schemes(self) -> Dict[str, Any]:
        """获取安全认证方案"""
        return {
            "BKAPIAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "x-bkapi-authorization",
                "description": "BlueKing API Gateway认证",
            }
        }

    def _generate_tags(self, collected_apis: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成标签信息"""
        tags = []
        tag_set = set()

        for module_name, module_info in collected_apis.items():
            if module_name not in tag_set:
                tags.append(
                    {
                        "name": module_name,
                        "description": module_info.get(
                            "description", f"{module_name} APIs"
                        ),
                    }
                )
                tag_set.add(module_name)

            for api_info in module_info["apis"]:
                for tag in api_info.get("tags", []):
                    if tag not in tag_set:
                        tags.append({"name": tag, "description": f"{tag} related APIs"})
                        tag_set.add(tag)

        return tags

    def _generate_path_info(
        self, module_name: str, api_info: Dict[str, Any]
    ) -> Optional[tuple]:
        """
        生成单个API的路径信息

        Args:
            module_name: 模块名称
            api_info: API信息

        Returns:
            tuple: (path, operation) 或 None
        """
        try:
            # 构建路径
            action = api_info.get("action", "")
            if not action:
                return None

            # 清理并标准化路径
            path = action.strip("/")
            if not path.startswith("/"):
                path = "/" + path

            # 构建操作信息
            operation = {
                "tags": [module_name] + api_info.get("tags", []),
                "summary": api_info.get("display_name", api_info["name"]),
                "description": api_info.get("description", ""),
                "operationId": f"{module_name}_{api_info['name']}",
                "deprecated": api_info.get("deprecated", False),
                "security": [{"BKAPIAuth": []}],
            }

            # 添加参数
            if api_info.get("request_schema"):
                if api_info["method"].upper() == "GET":
                    operation["parameters"] = self._schema_to_parameters(
                        api_info["request_schema"]
                    )
                else:
                    operation["requestBody"] = self._schema_to_request_body(
                        api_info["request_schema"]
                    )

            # 添加响应
            operation["responses"] = self._generate_responses(api_info)

            # 添加示例
            if api_info.get("examples"):
                examples = api_info["examples"]
                if "request" in examples:
                    if "requestBody" in operation:
                        operation["requestBody"]["content"]["application/json"][
                            "example"
                        ] = examples["request"]

            return path, operation

        except Exception as e:
            logger.warning(f"生成路径信息失败 {module_name}.{api_info['name']}: {e}")
            return None

    def _schema_to_parameters(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将schema转换为参数列表（用于GET请求）"""
        parameters = []

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for param_name, param_schema in properties.items():
            parameter = {
                "name": param_name,
                "in": "query",
                "required": param_name in required,
                "schema": param_schema,
            }

            if "description" in param_schema:
                parameter["description"] = param_schema["description"]

            parameters.append(parameter)

        return parameters

    def _schema_to_request_body(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """将schema转换为请求体"""
        return {"required": True, "content": {"application/json": {"schema": schema}}}

    def _generate_responses(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成响应信息"""
        responses = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "result": {
                                    "type": "boolean",
                                    "description": "请求是否成功",
                                },
                                "code": {"type": "integer", "description": "状态码"},
                                "message": {
                                    "type": "string",
                                    "description": "返回消息",
                                },
                                "data": api_info.get(
                                    "response_schema", {"type": "object"}
                                ),
                            },
                            "required": ["result", "code", "message"],
                        }
                    }
                },
            },
            "400": {
                "description": "Bad Request",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "result": {"type": "boolean", "example": False},
                                "code": {"type": "integer", "example": 400},
                                "message": {
                                    "type": "string",
                                    "example": "Invalid request parameters",
                                },
                            },
                        }
                    }
                },
            },
            "500": {
                "description": "Internal Server Error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "result": {"type": "boolean", "example": False},
                                "code": {"type": "integer", "example": 500},
                                "message": {
                                    "type": "string",
                                    "example": "Internal server error",
                                },
                            },
                        }
                    }
                },
            },
        }

        return responses
