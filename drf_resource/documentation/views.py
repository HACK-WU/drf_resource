# -*- coding: utf-8 -*-
"""
API文档视图

提供Web界面访问API文档的Django视图。
"""

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from drf_resource.documentation.generator import DocumentationGenerator
from drf_resource.documentation.settings import API_DOCS_SETTINGS
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class APIDocumentationView(TemplateView):
    """
    API文档主页面视图
    """

    template_name = "drf_resource/api_docs_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            generator = DocumentationGenerator()
            docs_data = generator.generate_documentation_data()
            context.update({"docs_data": docs_data, "settings": API_DOCS_SETTINGS})
        except Exception as e:
            logger.error(f"生成API文档数据失败: {e}")
            context.update({"error": str(e), "docs_data": None})

        return context


class APIDetailView(TemplateView):
    """
    API详情页面视图
    """

    template_name = "drf_resource/api_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        module_name = kwargs.get("module_name")
        api_name = kwargs.get("api_name")

        try:
            generator = DocumentationGenerator()
            docs_data = generator.generate_documentation_data()

            # 查找指定的API
            api_info = None
            module_info = None

            if module_name in docs_data["modules"]:
                module_info = docs_data["modules"][module_name]
                for api in module_info["apis"]:
                    if api["name"] == api_name:
                        api_info = api
                        break

            if not api_info:
                context["error"] = f"API {module_name}.{api_name} 未找到"
            else:
                context.update(
                    {
                        "api_info": api_info,
                        "module_info": module_info,
                        "docs_data": docs_data,
                    }
                )

        except Exception as e:
            logger.error(f"获取API详情失败: {e}")
            context["error"] = str(e)

        return context


@api_view(["GET"])
@permission_classes([AllowAny])
def openapi_schema_view(request):
    """
    返回OpenAPI格式的schema
    """
    try:
        generator = DocumentationGenerator()
        schema = generator.generate_openapi_schema()
        return Response(schema)
    except Exception as e:
        logger.error(f"生成OpenAPI schema失败: {e}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def api_docs_json_view(request):
    """
    返回JSON格式的API文档数据
    """
    try:
        generator = DocumentationGenerator()
        docs_data = generator.generate_documentation_data()
        return Response(docs_data)
    except Exception as e:
        logger.error(f"生成API文档数据失败: {e}")
        return Response({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class SwaggerUIView(TemplateView):
    """
    Swagger UI界面视图
    """

    template_name = "drf_resource/swagger_ui.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "swagger_settings": {
                    "title": API_DOCS_SETTINGS.get(
                        "TITLE", "DRF Resource API Documentation"
                    ),
                    "version": API_DOCS_SETTINGS.get("VERSION", "1.0.0"),
                    "description": API_DOCS_SETTINGS.get("DESCRIPTION", ""),
                    "schema_url": "/api-docs/openapi.json",
                }
            }
        )
        return context


class ReDocView(TemplateView):
    """
    ReDoc界面视图
    """

    template_name = "drf_resource/redoc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "redoc_settings": {
                    "title": API_DOCS_SETTINGS.get(
                        "TITLE", "DRF Resource API Documentation"
                    ),
                    "schema_url": "/api-docs/openapi.json",
                }
            }
        )
        return context


@api_view(["GET"])
@permission_classes([AllowAny])
def api_health_check(request):
    """
    API文档服务健康检查
    """
    try:
        generator = DocumentationGenerator()
        collected_apis = generator.collect_api_resources()

        return Response(
            {
                "status": "healthy",
                "total_modules": len(collected_apis),
                "total_apis": sum(
                    len(module["apis"]) for module in collected_apis.values()
                ),
                "settings": {
                    "enabled": API_DOCS_SETTINGS.get("ENABLED", False),
                    "auto_generate": API_DOCS_SETTINGS.get("AUTO_GENERATE", True),
                },
            }
        )
    except Exception as e:
        logger.error(f"API文档健康检查失败: {e}")
        return Response({"status": "unhealthy", "error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def regenerate_docs(request):
    """
    手动重新生成文档
    """
    if not API_DOCS_SETTINGS.get("ENABLED", False):
        return Response({"error": "API文档功能未启用"}, status=400)

    try:
        generator = DocumentationGenerator()

        # 重新收集API资源
        collected_apis = generator.collect_api_resources()

        # 生成文档数据
        docs_data = generator.generate_documentation_data()

        return Response(
            {
                "status": "success",
                "message": "文档重新生成成功",
                "stats": docs_data["stats"],
            }
        )
    except Exception as e:
        logger.error(f"重新生成文档失败: {e}")
        return Response({"status": "error", "message": str(e)}, status=500)
