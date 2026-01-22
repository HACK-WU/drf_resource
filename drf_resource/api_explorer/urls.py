from drf_resource.api_explorer.views import ApiHomeResourceViewSet
from drf_resource.routers import ResourceRouter

# 使用 ResourceRouter 注册 ViewSet
router = ResourceRouter()
router.register("api_home", ApiHomeResourceViewSet, basename="api_home")

urlpatterns = router.urls
