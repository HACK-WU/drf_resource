# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from drf_resource.api_explorer.exceptions import ResourceNotFoundError
from drf_resource.api_explorer.permissions import IsTestEnvironment
from drf_resource.api_explorer.services import APIDiscoveryService, APIInvokeService
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class IndexView(APIView):
    """
    API Explorer 主页面

    返回 HTML 页面（本次实现仅返回简单提示）
    """

    permission_classes = [IsTestEnvironment]

    def get(self, request):
        """
        获取主页面
        """
        # 本次实现暂时返回简单的 JSON 响应
        # 后续可以改为渲染 HTML 模板
        return Response(
            {
                'result': True,
                'message': 'API Explorer 主页面',
                'data': {
                    'title': 'API Explorer',
                    'description': '用于查看和调试项目中的 API 资源',
                    'endpoints': {
                        'catalog': '/api-explorer/catalog/',
                        'api_detail': '/api-explorer/api_detail/',
                        'invoke': '/api-explorer/invoke/',
                    },
                },
            }
        )


class CatalogView(APIView):
    """
    获取 API 目录列表
    """

    permission_classes = [IsTestEnvironment]

    class CatalogRequestSerializer(serializers.Serializer):
        """目录查询请求参数"""

        search = serializers.CharField(required=False, allow_blank=True, label="搜索关键词")
        module = serializers.CharField(required=False, allow_blank=True, label="模块名")

    def get(self, request):
        """
        获取 API 目录

        Query Parameters:
            - search: 搜索关键词（可选）
            - module: 过滤指定模块（可选）
        """
        # 参数校验
        serializer = self.CatalogRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {'result': False, 'message': '参数校验失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        # 获取参数
        search = serializer.validated_data.get('search', None)
        module_filter = serializer.validated_data.get('module', None)

        # 调用服务层
        try:
            data = APIDiscoveryService.discover_all_apis(search=search, module_filter=module_filter)

            return Response({'result': True, 'data': data, 'message': 'success'})

        except Exception as e:
            logger.error(f"获取 API 目录失败: {e}")
            return Response(
                {'result': False, 'message': f'获取 API 目录失败: {str(e)}', 'data': None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class APIDetailView(APIView):
    """
    获取 API 详细信息
    """

    permission_classes = [IsTestEnvironment]

    class APIDetailRequestSerializer(serializers.Serializer):
        """API 详情请求参数"""

        module = serializers.CharField(required=True, label="模块名")
        api_name = serializers.CharField(required=True, label="接口名")

    def get(self, request):
        """
        获取 API 详情

        Query Parameters:
            - module: 模块名（必填）
            - api_name: 接口名（必填）
        """
        # 参数校验
        serializer = self.APIDetailRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {'result': False, 'message': '参数校验失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        # 获取参数
        module = serializer.validated_data['module']
        api_name = serializer.validated_data['api_name']

        # 调用服务层
        try:
            data = APIDiscoveryService.get_api_detail(module, api_name)

            return Response({'result': True, 'data': data, 'message': 'success'})

        except ResourceNotFoundError as e:
            return Response({'result': False, 'message': str(e), 'data': None}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"获取 API 详情失败: {module}.{api_name}, 错误: {e}")
            return Response(
                {'result': False, 'message': f'获取 API 详情失败: {str(e)}', 'data': None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InvokeView(APIView):
    """
    在线调用 API
    """

    permission_classes = [IsTestEnvironment]

    class InvokeRequestSerializer(serializers.Serializer):
        """API 调用请求参数"""

        module = serializers.CharField(required=True, label="模块名")
        api_name = serializers.CharField(required=True, label="接口名")
        params = serializers.DictField(required=False, default=dict, label="请求参数")

    def post(self, request):
        """
        调用 API

        Request Body:
            - module: 模块名（必填）
            - api_name: 接口名（必填）
            - params: 请求参数（可选，JSON 对象）
        """
        # 参数校验
        serializer = self.InvokeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'result': False, 'message': '参数校验失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        # 获取参数
        module = serializer.validated_data['module']
        api_name = serializer.validated_data['api_name']
        params = serializer.validated_data.get('params', {})

        # 获取当前用户
        username = getattr(request.user, 'username', 'anonymous')

        # 调用服务层
        try:
            result = APIInvokeService.invoke_api(module, api_name, params, username)

            return Response(
                {'result': result['success'], 'data': result, 'message': '调用成功' if result['success'] else '调用失败'}
            )

        except ResourceNotFoundError as e:
            return Response({'result': False, 'message': str(e), 'data': None}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"API 调用异常: {module}.{api_name}, 错误: {e}")
            return Response(
                {'result': False, 'message': f'API 调用异常: {str(e)}', 'data': None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
