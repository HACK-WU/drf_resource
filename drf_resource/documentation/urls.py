# -*- coding: utf-8 -*-
"""
API文档URL配置
"""

from django.urls import path

from . import views

app_name = "api_docs"

urlpatterns = [
    # 主要文档页面
    path("", views.APIDocumentationView.as_view(), name="index"),
    path(
        "api/<str:module_name>/<str:api_name>/",
        views.APIDetailView.as_view(),
        name="api_detail",
    ),
    # OpenAPI相关
    path("openapi.json", views.openapi_schema_view, name="openapi_schema"),
    path("swagger/", views.SwaggerUIView.as_view(), name="swagger_ui"),
    path("redoc/", views.ReDocView.as_view(), name="redoc"),
    # API数据接口
    path("api-data.json", views.api_docs_json_view, name="api_docs_json"),
    # 管理接口
    path("health/", views.api_health_check, name="health_check"),
    path("regenerate/", views.regenerate_docs, name="regenerate_docs"),
]
