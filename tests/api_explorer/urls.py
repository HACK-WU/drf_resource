"""
测试用 URL 配置
"""

from drf_resource.api_explorer.views import ApiHomeResourceViewSet
from drf_resource.views.routers import ResourceRouter

router = ResourceRouter()
router.register("api-explorer", ApiHomeResourceViewSet, basename="api-explorer")

urlpatterns = router.urls
