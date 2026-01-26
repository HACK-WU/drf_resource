from django.urls import path
from django.http import JsonResponse

from drf_resource.api_explorer.views import ApiHomeResourceViewSet
from drf_resource.routers import ResourceRouter

# 使用 ResourceRouter 注册 ViewSet
router = ResourceRouter()
router.register("api_resource", ApiHomeResourceViewSet, basename="api-resource")

# drf-spectacular 文档路由（可选，需安装 drf-spectacular）
try:
    from drf_resource.contrib.spectacular import (
        FilterableSpectacularAPIView,
        FilterableSwaggerView,
        FilterableSpectacularRedocView,
        ApiTagsView,
        ApiDocsView,
        clear_schema_cache,
    )

    def debug_clear_cache(request):
        """清除 schema 缓存的调试端点"""
        clear_schema_cache()
        return JsonResponse(
            {"success": True, "message": "Schema 缓存已清除，请刷新页面"}
        )

    spectacular_urlpatterns = [
        # OpenAPI Schema (支持标签过滤和缓存)
        path("schema/", FilterableSpectacularAPIView.as_view(), name="schema"),
        # 支持标签过滤的 Swagger UI
        path(
            "docs/swagger/",
            FilterableSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        # API 标签统计接口
        path("docs/tags/", ApiTagsView.as_view(), name="api-tags"),
        # API 文档正式版页面
        path("docs/", ApiDocsView.as_view(), name="api-docs"),
        # ReDoc（支持缓存和标签过滤）
        path(
            "redoc/",
            FilterableSpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        # 调试：清除缓存
        path("docs/clear-cache/", debug_clear_cache, name="clear-cache"),
    ]
except ImportError:
    spectacular_urlpatterns = []

urlpatterns = router.urls + spectacular_urlpatterns
