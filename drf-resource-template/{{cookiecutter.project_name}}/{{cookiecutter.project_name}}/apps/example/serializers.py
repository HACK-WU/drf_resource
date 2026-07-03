"""示例 Serializer"""
from rest_framework import serializers

class ExampleRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, help_text="名称")

class ExampleResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID")
    name = serializers.CharField(help_text="名称")
    message = serializers.CharField(help_text="响应消息")
