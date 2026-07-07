from django.urls import include, path

from drf_resource.api_explorer.views import ApiHomeResourceViewSet
from drf_resource.views.routers import ResourceRouter

# 使用 ResourceRouter 注册 ViewSet
router = ResourceRouter()
router.register("api_resource", ApiHomeResourceViewSet, basename="api-resource")

# drf-spectacular 文档路由统一由 drf_resource.contrib.urls 提供
# 使用 drf_resource_docs 命名空间，避免与项目中已有 URL name 冲突
# 如需自定义文档路由，请直接 include("drf_resource.contrib.urls")
try:
    spectacular_urlpatterns = [
        path("", include("drf_resource.contrib.urls")),
    ]
except ImportError:
    spectacular_urlpatterns = []

urlpatterns = router.urls + spectacular_urlpatterns
