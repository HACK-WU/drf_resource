"""URL 路由配置"""
from django.contrib import admin
from django.urls import path, include
from drf_resource.views.routers import ResourceRouter
from {{ cookiecutter.project_name }}.apps.example.viewsets import ExampleViewSet
{% if cookiecutter.enable_api_docs == "yes" %}
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
{% endif %}

router = ResourceRouter()
router.register("example", ExampleViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    {% if cookiecutter.enable_api_docs == "yes" %}
    # API 文档
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    {% endif %}
]
