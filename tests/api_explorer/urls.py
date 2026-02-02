"""
测试用 URL 配置
"""

from django.urls import path

# 导入 API explorer views
from drf_resource.api_explorer.views import (
    HomeView,
    IndexView,
    CatalogView,
    APIDetailView,
    InvokeView,
    ModulesView,
)

urlpatterns = [
    path("api-explorer/", IndexView.as_view(), name="api-explorer-index"),
    path("api-explorer/home/", HomeView.as_view(), name="api-explorer-home"),
    path("api-explorer/catalog/", CatalogView.as_view(), name="api-explorer-catalog"),
    path(
        "api-explorer/api_detail/", APIDetailView.as_view(), name="api-explorer-detail"
    ),
    path("api-explorer/invoke/", InvokeView.as_view(), name="api-explorer-invoke"),
    path(
        "api-explorer/api_modules/", ModulesView.as_view(), name="api-explorer-modules"
    ),
]
