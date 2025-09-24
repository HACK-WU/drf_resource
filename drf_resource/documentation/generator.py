# -*- coding: utf-8 -*-
"""
API文档生成器

该模块实现从DRF Resource框架收集API信息并生成文档的核心功能。
"""

import logging
from collections import defaultdict
from typing import Any, Dict, Optional


try:
    from drf_spectacular.openapi import AutoSchema
    from drf_spectacular.utils import extend_schema
except ImportError:
    # 如果导入失败，创建 mock 类
    class AutoSchema:
        pass

    def extend_schema(**kwargs):
        def decorator(func):
            return func

        return decorator


from ..management.root import api
from .schema import APIResourceSchema
from .settings import API_DOCS_SETTINGS

logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """
    API文档生成器

    负责从api对象收集已注册的API资源，提取元数据，
    并生成结构化的文档数据。
    """

    def __init__(self):
        self.collected_apis = {}
        self.api_modules = {}
        self.schema_generator = APIResourceSchema()

    def collect_api_resources(self) -> Dict[str, Any]:
        """
        从api对象收集所有已注册的API资源

        Returns:
            Dict: 收集到的API资源信息
        """
        logger.info("开始收集API资源...")

        collected = {}

        # 遍历api对象的所有属性
        for attr_name in dir(api):
            if attr_name.startswith("_"):
                continue

            try:
                attr_value = getattr(api, attr_name)
                # 检查是否是APIResourceShortcut实例
                from ..management.root import APIResourceShortcut

                if isinstance(attr_value, APIResourceShortcut):
                    module_info = self._extract_module_info(attr_name, attr_value)
                    if module_info:
                        collected[attr_name] = module_info
                        logger.debug(f"收集到API模块: {attr_name}")

            except Exception as e:
                logger.warning(f"收集API模块 {attr_name} 时出错: {e}")
                continue

        self.collected_apis = collected
        logger.info(f"API资源收集完成，共收集到 {len(collected)} 个模块")
        return collected

    def _extract_module_info(
        self, module_name: str, resource_shortcut
    ) -> Optional[Dict[str, Any]]:
        """
        提取API模块信息

        Args:
            module_name: 模块名称
            resource_shortcut: APIResourceShortcut实例

        Returns:
            Dict: 模块信息，包含APIs列表
        """
        try:
            # 触发资源加载
            if not resource_shortcut.loaded:
                resource_shortcut._setup()

            module_info = {
                "name": module_name,
                "display_name": self._get_module_display_name(module_name),
                "description": self._get_module_description(resource_shortcut),
                "base_url": self._get_module_base_url(resource_shortcut),
                "apis": [],
            }

            # 遍历模块中的所有方法
            for method_name in resource_shortcut.list_method():
                try:
                    method_obj = getattr(resource_shortcut, method_name)
                    if hasattr(method_obj, "__class__"):
                        api_info = self._extract_api_info(method_name, method_obj)
                        if api_info:
                            module_info["apis"].append(api_info)
                except Exception as e:
                    logger.warning(f"提取API信息失败 {module_name}.{method_name}: {e}")
                    continue

            return module_info if module_info["apis"] else None

        except Exception as e:
            logger.error(f"提取模块信息失败 {module_name}: {e}")
            return None

    def _extract_api_info(
        self, method_name: str, resource_instance
    ) -> Optional[Dict[str, Any]]:
        """
        提取单个API的信息

        Args:
            method_name: 方法名称
            resource_instance: Resource实例

        Returns:
            Dict: API信息
        """
        try:
            resource_class = resource_instance.__class__

            # 检查是否应该包含在文档中
            if getattr(resource_class, "doc_hidden", False):
                return None

            api_info = {
                "name": method_name,
                "display_name": getattr(resource_class, "api_name", None)
                or self._format_display_name(method_name),
                "description": getattr(resource_class, "api_description", None)
                or getattr(resource_class, "__doc__", ""),
                "category": getattr(resource_class, "api_category", "external"),
                "version": getattr(resource_class, "api_version", "v1"),
                "tags": getattr(resource_class, "api_tags", []),
                "deprecated": getattr(resource_class, "deprecated", False),
                "deprecation_message": getattr(
                    resource_class, "deprecation_message", None
                ),
                "rate_limit": getattr(resource_class, "rate_limit", None),
                "method": getattr(resource_class, "method", "GET").upper(),
                "action": getattr(resource_class, "action", ""),
                "timeout": getattr(resource_class, "TIMEOUT", 60),
                "examples": getattr(resource_class, "doc_examples", {}),
                "request_schema": self._get_request_schema(resource_class),
                "response_schema": self._get_response_schema(resource_class),
                "class_path": f"{resource_class.__module__}.{resource_class.__qualname__}",
            }

            return api_info

        except Exception as e:
            logger.error(f"提取API信息失败 {method_name}: {e}")
            return None

    def _get_request_schema(self, resource_class) -> Dict[str, Any]:
        """获取请求参数schema"""
        try:
            if (
                hasattr(resource_class, "RequestSerializer")
                and resource_class.RequestSerializer
            ):
                return self.schema_generator.extract_serializer_schema(
                    resource_class.RequestSerializer
                )
        except Exception as e:
            logger.warning(f"获取请求schema失败: {e}")
        return {}

    def _get_response_schema(self, resource_class) -> Dict[str, Any]:
        """获取响应参数schema"""
        try:
            if (
                hasattr(resource_class, "ResponseSerializer")
                and resource_class.ResponseSerializer
            ):
                return self.schema_generator.extract_serializer_schema(
                    resource_class.ResponseSerializer
                )
        except Exception as e:
            logger.warning(f"获取响应schema失败: {e}")
        return {}

    def _get_module_display_name(self, module_name: str) -> str:
        """获取模块显示名称"""
        return module_name.replace("_", " ").title()

    def _get_module_description(self, resource_shortcut) -> str:
        """获取模块描述"""
        try:
            if hasattr(resource_shortcut, "_package") and resource_shortcut._package:
                return getattr(resource_shortcut._package, "__doc__", "") or ""
        except:
            pass
        return ""

    def _get_module_base_url(self, resource_shortcut) -> str:
        """获取模块基础URL"""
        try:
            # 尝试从第一个API资源获取base_url
            for method_name in resource_shortcut.list_method():
                method_obj = getattr(resource_shortcut, method_name)
                if hasattr(method_obj, "__class__"):
                    resource_class = method_obj.__class__
                    if hasattr(resource_class, "base_url"):
                        return resource_class.base_url
        except:
            pass
        return ""

    def _format_display_name(self, method_name: str) -> str:
        """格式化显示名称"""
        return method_name.replace("_", " ").title()

    def generate_openapi_schema(self) -> Dict[str, Any]:
        """
        生成OpenAPI格式的schema

        Returns:
            Dict: OpenAPI格式的API文档
        """
        if not self.collected_apis:
            self.collect_api_resources()

        return self.schema_generator.generate_openapi_schema(self.collected_apis)

    def generate_documentation_data(self) -> Dict[str, Any]:
        """
        生成用于文档页面的数据

        Returns:
            Dict: 包含所有文档数据的字典
        """
        if not self.collected_apis:
            self.collect_api_resources()

        # 按分类组织API
        categorized_apis = defaultdict(list)
        all_tags = set()

        for module_name, module_info in self.collected_apis.items():
            for api_info in module_info["apis"]:
                category = api_info.get("category", "external")
                categorized_apis[category].append(
                    {
                        "module": module_name,
                        "module_info": module_info,
                        "api_info": api_info,
                    }
                )
                all_tags.update(api_info.get("tags", []))

        return {
            "title": API_DOCS_SETTINGS.get("TITLE", "DRF Resource API Documentation"),
            "version": API_DOCS_SETTINGS.get("VERSION", "1.0.0"),
            "description": API_DOCS_SETTINGS.get(
                "DESCRIPTION",
                "Auto-generated API documentation for DRF Resource framework",
            ),
            "modules": self.collected_apis,
            "categorized_apis": dict(categorized_apis),
            "all_tags": sorted(all_tags),
            "stats": {
                "total_modules": len(self.collected_apis),
                "total_apis": sum(
                    len(module["apis"]) for module in self.collected_apis.values()
                ),
                "categories": list(categorized_apis.keys()),
            },
        }
