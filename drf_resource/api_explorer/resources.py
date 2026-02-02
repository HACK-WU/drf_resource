import logging

from django.shortcuts import render
from django.urls import reverse
from rest_framework import serializers

from drf_resource.resources.base import Resource
from drf_resource.api_explorer.services import APIDiscoveryService, APIInvokeService


logger = logging.getLogger(__name__)


class HomeResource(Resource):
    """
    API Explorer 主页渲染

    渲染 API Explorer 的前端页面（返回 HTML）
    """

    def perform_request(self, validated_request_data):
        """
        渲染主页面

        注意：此 Resource 返回 HttpResponse 对象，需在 ViewSet 中特殊处理
        """

        return render(self._current_request, "api_explorer/index.html")


class InfoResource(Resource):
    """
    API Explorer 基本信息

    返回 API Explorer 的基本信息和可用端点的参数说明
    """

    def perform_request(self, validated_request_data):
        """
        获取 API Explorer 基本信息

        返回所有可用端点的访问路径和参数说明
        """
        request = self._current_request

        # 使用反向解析获取 URL，并构建完整的绝对 URL
        try:
            api_list_url = request.build_absolute_uri(
                reverse("api_explorer:api_home-api_list")
            )
            api_detail_url = request.build_absolute_uri(
                reverse("api_explorer:api_home-api_detail")
            )
            api_invoke_url = request.build_absolute_uri(
                reverse("api_explorer:api_home-api_invoke")
            )
            module_list_url = request.build_absolute_uri(
                reverse("api_explorer:api_home-module_list")
            )
        except Exception as e:
            # 如果反向解析失败，记录错误并使用相对路径
            logger.warning(f"URL 反向解析失败: {e}")
            base_path = request.path.rstrip("/").rsplit("/", 1)[0] + "/"
            api_list_url = request.build_absolute_uri(base_path + "api_list/")
            api_detail_url = request.build_absolute_uri(base_path + "api_detail/")
            api_invoke_url = request.build_absolute_uri(base_path + "api_invoke/")
            module_list_url = request.build_absolute_uri(base_path + "module_list/")

        return {
            "title": "API Explorer",
            "description": "用于查看和调试项目中的 API 资源",
            "endpoints": {
                "api_list": api_list_url,
                "api_detail": api_detail_url,
                "api_invoke": api_invoke_url,
                "module_list": module_list_url,
            },
            "endpoints_info": [
                {
                    "name": "api_list",
                    "url": api_list_url,
                    "method": "GET",
                    "description": "获取 API 目录列表，支持搜索和模块过滤",
                    "params": [
                        {
                            "name": "search",
                            "type": "string",
                            "required": False,
                            "description": "搜索关键词，匹配模块名、接口名、类名、标签",
                            "default": None,
                        },
                        {
                            "name": "module",
                            "type": "string",
                            "required": False,
                            "description": "过滤指定模块",
                            "default": None,
                        },
                    ],
                },
                {
                    "name": "api_detail",
                    "url": api_detail_url,
                    "method": "GET",
                    "description": "获取单个 API 的详细信息，包括请求/响应参数结构",
                    "params": [
                        {
                            "name": "module",
                            "type": "string",
                            "required": True,
                            "description": "模块名",
                            "default": None,
                        },
                        {
                            "name": "api_name",
                            "type": "string",
                            "required": True,
                            "description": "API 名称",
                            "default": None,
                        },
                    ],
                },
                {
                    "name": "api_invoke",
                    "url": api_invoke_url,
                    "method": "POST",
                    "description": "在线调用指定的第三方 API，并返回调用结果",
                    "params": [
                        {
                            "name": "module",
                            "type": "string",
                            "required": True,
                            "description": "模块名",
                            "default": None,
                        },
                        {
                            "name": "api_name",
                            "type": "string",
                            "required": True,
                            "description": "API 名称",
                            "default": None,
                        },
                        {
                            "name": "params",
                            "type": "object",
                            "required": False,
                            "description": "请求参数（JSON 对象）",
                            "default": {},
                        },
                    ],
                },
                {
                    "name": "module_list",
                    "url": module_list_url,
                    "method": "GET",
                    "description": "获取所有可用的模块列表，支持模糊查询",
                    "params": [
                        {
                            "name": "search",
                            "type": "string",
                            "required": False,
                            "description": "搜索关键词，匹配模块名或展示名称",
                            "default": None,
                        },
                    ],
                },
            ],
        }


class ApiListResource(Resource):
    """
    API 目录列表

    获取所有 API 的目录列表，支持搜索和模块过滤
    """

    class RequestSerializer(serializers.Serializer):
        """API 目录列表请求参数"""

        search = serializers.CharField(
            required=False, allow_blank=True, label="搜索关键词"
        )
        module = serializers.CharField(required=False, allow_blank=True, label="模块名")

    def perform_request(self, validated_request_data):
        """
        获取 API 目录

        Args:
            validated_request_data: 包含 search 和 module 参数

        Returns:
            API 目录数据
        """
        search = validated_request_data.get("search") or None
        module_filter = validated_request_data.get("module") or None

        # 调用服务层
        data = APIDiscoveryService.discover_all_apis(
            search=search, module_filter=module_filter
        )
        return data


class ApiDetailRequestSerializer(serializers.Serializer):
    """API 详情请求参数"""

    module = serializers.CharField(required=True, label="模块名")
    api_name = serializers.CharField(required=True, label="接口名")


class ApiDetailResource(Resource):
    """
    API 详情

    获取单个 API 的详细信息，包括请求/响应参数结构
    """

    RequestSerializer = ApiDetailRequestSerializer

    def perform_request(self, validated_request_data):
        """
        获取 API 详情

        Args:
            validated_request_data: 包含 module 和 api_name 参数

        Returns:
            API 详细信息

        Raises:
            ResourceNotFoundError: API 不存在
        """
        module = validated_request_data["module"]
        api_name = validated_request_data["api_name"]

        # 调用服务层
        data = APIDiscoveryService.get_api_detail(module, api_name)
        return data


class ApiInvokeRequestSerializer(serializers.Serializer):
    """API 调用请求参数"""

    module = serializers.CharField(required=True, label="模块名")
    api_name = serializers.CharField(required=True, label="接口名")
    params = serializers.DictField(required=False, default=dict, label="请求参数")


class ApiInvokeResource(Resource):
    """
    API 调用

    在线调用指定的第三方 API，并返回调用结果
    """

    RequestSerializer = ApiInvokeRequestSerializer

    def perform_request(self, validated_request_data):
        """
        调用 API

        Args:
            validated_request_data: 包含 module、api_name 和 params 参数

        Returns:
            API 调用结果

        Raises:
            ResourceNotFoundError: API 不存在
        """
        module = validated_request_data["module"]
        api_name = validated_request_data["api_name"]
        params = validated_request_data.get("params", {})

        # 获取当前用户
        request = self._current_request
        username = (
            getattr(request.user, "username", "anonymous") if request else "anonymous"
        )

        # 调用服务层
        result = APIInvokeService.invoke_api(module, api_name, params, username)
        return result


class ModuleListRequestSerializer(serializers.Serializer):
    """模块列表请求参数"""

    search = serializers.CharField(required=False, allow_blank=True, label="搜索关键词")


class ModuleListResource(Resource):
    """
    模块列表

    获取所有可用的模块列表，支持模糊查询
    """

    RequestSerializer = ModuleListRequestSerializer

    def perform_request(self, validated_request_data):
        """
        获取所有模块列表

        Args:
            validated_request_data: 包含 search 参数

        Returns:
            模块列表数据
        """
        search = validated_request_data.get("search") or None

        # 调用服务层
        data = APIDiscoveryService.get_all_modules(search=search)
        return data
