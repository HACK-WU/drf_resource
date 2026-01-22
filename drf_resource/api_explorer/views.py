from drf_resource.api_explorer.permissions import IsTestEnvironment
from drf_resource.api_explorer.resources import (
    ApiDetailResource,
    ApiInvokeResource,
    ApiListResource,
    HomeResource,
    InfoResource,
    ModuleListResource,
)
from drf_resource.viewsets import ResourceRoute, ResourceViewSet


class ApiHomeResourceViewSet(ResourceViewSet):
    """
    API Explorer 统一视图集

    通过 resource_routes 配置不同的 endpoint 实现所有 API Explorer 功能：
    - api_home/          : 主页渲染 (GET)
    - api_home/info/     : 基本信息 (GET)
    - api_home/api_list/ : API 目录列表 (GET)
    - api_home/api_detail/: API 详情 (GET)
    - api_home/api_invoke/: API 调用 (POST)
    - api_home/module_list/: 模块列表 (GET)
    """

    permission_classes = [IsTestEnvironment]

    resource_routes = [
        # 主页渲染 - endpoint 为空，映射到 list 方法
        ResourceRoute("GET", HomeResource),
        # 基本信息
        ResourceRoute("GET", InfoResource, endpoint="api_info"),
        # API 目录列表
        ResourceRoute("GET", ApiListResource, endpoint="api_list"),
        # API 详情
        ResourceRoute("GET", ApiDetailResource, endpoint="api_detail"),
        # API 调用
        ResourceRoute("POST", ApiInvokeResource, endpoint="api_invoke"),
        # 模块列表
        ResourceRoute("GET", ModuleListResource, endpoint="module_list"),
    ]
