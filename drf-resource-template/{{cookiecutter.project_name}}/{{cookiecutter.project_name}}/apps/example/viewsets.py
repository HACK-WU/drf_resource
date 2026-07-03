"""示例 ViewSet"""
from drf_resource.views.viewsets import ResourceViewSet, ResourceRoute
from {{ cookiecutter.project_name }}.apps.example.resources import ExampleResource

class ExampleViewSet(ResourceViewSet):
    """
    示例接口

    提供 GET /api/example/ 端点，返回问候消息。
    """
    resource_routes = [
        ResourceRoute(
            method="GET",
            resource_class=ExampleResource,
        ),
    ]
