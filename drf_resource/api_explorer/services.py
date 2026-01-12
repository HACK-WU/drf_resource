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
import time
from datetime import datetime
from typing import Dict, List, Optional

from drf_resource.api_explorer.exceptions import ResourceNotFoundError
from drf_resource.management.root import APIResourceShortcut, api

logger = logging.getLogger(__name__)


class APIDiscoveryService:
    """API 发现服务：扫描并提取 API 资源的元数据"""

    @classmethod
    def discover_all_apis(cls, search: Optional[str] = None, module_filter: Optional[str] = None) -> Dict:
        """
        发现所有 API 资源

        Args:
            search: 搜索关键词（匹配模块名、接口名、描述）
            module_filter: 过滤指定模块

        Returns:
            {
                "modules": [
                    {
                        "name": "bkdata",
                        "display_name": "计算平台",
                        "apis": [...]
                    }
                ],
                "total": 156
            }
        """
        modules = []

        try:
            # 遍历 api 命名空间
            for module_name in dir(api):
                # 跳过私有属性
                if module_name.startswith('_'):
                    continue

                try:
                    module_obj = getattr(api, module_name)

                    # 判断是否为 APIResourceShortcut
                    if not isinstance(module_obj, APIResourceShortcut):
                        continue

                    # 应用模块过滤
                    if module_filter and module_name != module_filter:
                        continue

                    # 获取该模块下的所有 API
                    apis = cls._extract_module_apis(module_name, module_obj, search)

                    if apis:
                        modules.append(
                            {'name': module_name, 'display_name': cls._get_display_name(module_obj), 'apis': apis}
                        )

                except Exception as e:
                    logger.warning(f"提取模块 {module_name} 的 API 失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"发现 API 资源失败: {e}")
            return {'modules': [], 'total': 0}

        return {'modules': modules, 'total': sum(len(m['apis']) for m in modules)}

    @classmethod
    def _extract_module_apis(
        cls, module_name: str, module_obj: APIResourceShortcut, search: Optional[str]
    ) -> List[Dict]:
        """
        提取模块下的所有 API

        Args:
            module_name: 模块名
            module_obj: APIResourceShortcut 实例
            search: 搜索关键词

        Returns:
            API 元数据列表
        """
        apis = []

        try:
            # 获取该模块下的所有 API 名称
            for api_name in module_obj.list_method():
                try:
                    # 获取 Resource 类
                    resource_class = module_obj._methods.get(api_name)

                    if resource_class is None:
                        continue

                    # 提取元数据
                    metadata = cls._extract_metadata(module_name, api_name, resource_class)

                    # 应用搜索过滤
                    if search and not cls._match_search(metadata, search):
                        continue

                    apis.append(metadata)

                except Exception as e:
                    logger.warning(f"提取 API {module_name}.{api_name} 的元数据失败: {e}")
                    continue

        except Exception as e:
            logger.warning(f"获取模块 {module_name} 的方法列表失败: {e}")

        return apis

    @classmethod
    def _extract_metadata(cls, module: str, api_name: str, resource_class) -> Dict:
        """
        提取 Resource 元数据

        Args:
            module: 模块名
            api_name: API 名称
            resource_class: Resource 类

        Returns:
            API 元数据字典
        """
        try:
            # 创建实例以访问属性
            instance = resource_class()

            # 提取基本信息
            label = getattr(instance, 'label', '') or getattr(resource_class, '__doc__', '') or ''
            label = label.strip() if label else api_name

            method = getattr(instance, 'method', 'GET')
            base_url = getattr(instance, 'base_url', '')
            action = getattr(instance, 'action', '')

            return {
                'name': api_name,
                'class_name': resource_class.__name__,
                'module': module,
                'label': label,
                'method': method.upper() if method else 'GET',
                'base_url': base_url,
                'action': action,
                'full_url': cls._build_full_url(base_url, action),
                'has_request_serializer': instance.RequestSerializer is not None,
                'has_response_serializer': instance.ResponseSerializer is not None,
            }
        except Exception as e:
            logger.warning(f"提取 {module}.{api_name} 元数据失败: {e}")
            # 返回最小元数据
            return {
                'name': api_name,
                'class_name': resource_class.__name__,
                'module': module,
                'label': api_name,
                'method': 'GET',
                'base_url': '',
                'action': '',
                'full_url': '',
                'has_request_serializer': False,
                'has_response_serializer': False,
            }

    @classmethod
    def _build_full_url(cls, base_url: str, action: str) -> str:
        """
        拼接完整 URL

        Args:
            base_url: 基础 URL
            action: 动作路径

        Returns:
            完整 URL
        """
        if not base_url or not action:
            return ''

        base = base_url.rstrip('/')
        act = action.lstrip('/')
        return f"{base}/{act}"

    @classmethod
    def _get_display_name(cls, module_obj: APIResourceShortcut) -> str:
        """
        获取模块的展示名称

        Args:
            module_obj: APIResourceShortcut 实例

        Returns:
            展示名称
        """
        try:
            # 尝试从模块的第一个 Resource 获取 module_name 属性
            methods = module_obj.list_method()
            if methods:
                first_method = methods[0]
                resource_class = module_obj._methods.get(first_method)
                if resource_class:
                    instance = resource_class()
                    module_name = getattr(instance, 'module_name', None)
                    if module_name:
                        return module_name
        except Exception:
            pass

        # 默认使用模块名
        return module_obj._path.split('.')[-2] if '.' in module_obj._path else module_obj._path

    @classmethod
    def _match_search(cls, metadata: Dict, search: str) -> bool:
        """
        检查元数据是否匹配搜索关键词

        Args:
            metadata: API 元数据
            search: 搜索关键词

        Returns:
            是否匹配
        """
        search_lower = search.lower()

        # 匹配模块名、接口名、类名、标签
        return (
            search_lower in metadata.get('module', '').lower()
            or search_lower in metadata.get('name', '').lower()
            or search_lower in metadata.get('class_name', '').lower()
            or search_lower in metadata.get('label', '').lower()
        )

    @classmethod
    def get_api_detail(cls, module: str, api_name: str) -> Dict:
        """
        获取单个 API 的详细信息（包含请求/响应字段结构）

        Args:
            module: 模块名
            api_name: API 名称

        Returns:
            API 详细信息

        Raises:
            ResourceNotFoundError: API 不存在
        """
        try:
            # 获取模块对象
            module_obj = getattr(api, module, None)
            if module_obj is None or not isinstance(module_obj, APIResourceShortcut):
                raise ResourceNotFoundError(f"模块不存在: {module}")

            # 获取 Resource 类
            resource_class = module_obj._methods.get(api_name)
            if resource_class is None:
                raise ResourceNotFoundError(f"API 不存在: {module}.{api_name}")

            # 提取基本元数据
            instance = resource_class()
            label = getattr(instance, 'label', '') or getattr(resource_class, '__doc__', '') or ''
            label = label.strip() if label else api_name

            method = getattr(instance, 'method', 'GET')
            base_url = getattr(instance, 'base_url', '')
            action = getattr(instance, 'action', '')

            # 生成文档（请求/响应参数结构）
            doc_data = {}
            try:
                doc_data = resource_class.generate_doc()
            except Exception as e:
                logger.warning(f"生成 {module}.{api_name} 的文档失败: {e}")
                doc_data = {'request_params': [], 'response_params': []}

            return {
                'module': module,
                'api_name': api_name,
                'class_name': resource_class.__name__,
                'label': label,
                'method': method.upper() if method else 'GET',
                'full_url': cls._build_full_url(base_url, action),
                'doc': label,
                'request_params': doc_data.get('request_params', []),
                'response_params': doc_data.get('response_params', []),
            }

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取 API 详情失败: {module}.{api_name}, 错误: {e}")
            raise ResourceNotFoundError(f"获取 API 详情失败: {str(e)}")


class APIInvokeService:
    """API 调用服务：动态调用第三方 API"""

    @classmethod
    def invoke_api(cls, module: str, api_name: str, params: dict, username: str) -> Dict:
        """
        调用指定的 API

        Args:
            module: 模块名
            api_name: API 名称
            params: 请求参数
            username: 调用用户

        Returns:
            {
                "success": True/False,
                "response": {...},
                "error_message": "...",
                "error_code": "...",
                "duration": 1.23,
                "request_params": {...},
                "timestamp": "2026-01-12T10:30:00Z"
            }
        """
        start_time = time.time()
        result = {
            'success': False,
            'response': None,
            'error_message': None,
            'error_code': None,
            'duration': 0,
            'request_params': cls._mask_sensitive(params.copy() if params else {}),
            'timestamp': datetime.now().isoformat(),
        }

        try:
            # 获取 Resource 实例
            resource = cls._get_resource(module, api_name)

            # 构建调用参数
            call_params = params.copy() if params else {}
            if username:
                call_params['bk_username'] = username

            # 调用 API
            response = resource.request(call_params)

            result['success'] = True
            result['response'] = response

            logger.info(f"API 调用成功: {module}.{api_name}, 用户: {username}")

        except AttributeError as e:
            result['error_message'] = f"API 不存在: {module}.{api_name}"
            result['error_code'] = "404"
            logger.warning(f"API 不存在: {module}.{api_name}, 错误: {e}")

        except Exception as e:
            # 尝试从异常中提取错误信息
            error_message = str(e)
            error_code = getattr(e, 'code', None)

            # 检查是否是 BKAPIError
            if hasattr(e, 'result'):
                result_data = getattr(e, 'result', {})
                if isinstance(result_data, dict):
                    error_message = result_data.get('message', error_message)
                    error_code = result_data.get('code', error_code)

            result['error_message'] = error_message
            result['error_code'] = str(error_code) if error_code else None

            logger.error(f"API 调用失败: {module}.{api_name}, 用户: {username}, 错误: {e}")

        finally:
            result['duration'] = round(time.time() - start_time, 3)

        return result

    @classmethod
    def _get_resource(cls, module: str, api_name: str):
        """
        动态获取 Resource 实例

        Args:
            module: 模块名
            api_name: API 名称

        Returns:
            Resource 实例

        Raises:
            ResourceNotFoundError: API 不存在
        """
        try:
            module_obj = getattr(api, module)
            resource = getattr(module_obj, api_name)
            return resource
        except AttributeError:
            raise ResourceNotFoundError(f"API 不存在: {module}.{api_name}")

    @classmethod
    def _mask_sensitive(cls, params: dict) -> dict:
        """
        脱敏敏感参数

        Args:
            params: 请求参数

        Returns:
            脱敏后的参数
        """
        if not params:
            return {}

        sensitive_keys = ['bk_app_secret', 'password', 'token', 'secret', 'passwd', 'key']
        masked = params.copy()

        for key in list(masked.keys()):
            # 检查键名是否包含敏感词
            if any(s in key.lower() for s in sensitive_keys):
                value = str(masked[key])
                if len(value) > 8:
                    masked[key] = value[:4] + '***' + value[-4:]
                else:
                    masked[key] = '***'

        return masked
