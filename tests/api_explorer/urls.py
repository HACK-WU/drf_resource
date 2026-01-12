# -*- coding: utf-8 -*-
"""
测试用 URL 配置
"""

from django.urls import path

# 导入 API explorer views
from drf_resource.api_explorer.views import (
    IndexView,
    CatalogView,
    APIDetailView,
    InvokeView,
)

urlpatterns = [
    path("api-explorer/", IndexView.as_view(), name="api-explorer-index"),
    path("api-explorer/catalog/", CatalogView.as_view(), name="api-explorer-catalog"),
    path(
        "api-explorer/api_detail/", APIDetailView.as_view(), name="api-explorer-detail"
    ),
    path("api-explorer/invoke/", InvokeView.as_view(), name="api-explorer-invoke"),
]
