"""示例 Resource"""
from drf_resource.resources.base import Resource
from {{ cookiecutter.project_name }}.apps.example.serializers import (
    ExampleRequestSerializer,
    ExampleResponseSerializer,
)

class ExampleResource(Resource):
    """
    示例资源 - 演示 drf_resource 的基本用法

    接收一个 name 参数，返回一条问候消息。
    """
    RequestSerializer = ExampleRequestSerializer
    ResponseSerializer = ExampleResponseSerializer

    def perform_request(self, validated_request_data):
        # 演示用：返回硬编码数据。实际项目中应从数据库获取。
        name = validated_request_data["name"]
        return {
            "id": 1,  # 演示值，实际应从数据库自增 ID 获取
            "name": name,
            "message": f"Hello, {name}! This is powered by drf_resource.",
        }
