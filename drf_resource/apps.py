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

from django.apps import AppConfig

from .documentation.settings import API_DOCS_SETTINGS
from .management.root import setup


# AppConfig 相关文档：https://docs.djangoproject.com/zh-hans/5.1/ref/applications/
class DRFResourceConfig(AppConfig):
    name = "drf_resource"
    verbose_name = "drf_resource"
    label = "drf_resource"

    def ready(self):
        """
        自动发现项目下resource和adapter和api
            cc
            ├── adapter
            │   ├── default.py
            │       ├── community
            │       │       └── resources.py
            │       └── enterprise
            │           └── resources.py
            └── resources.py
            使用:
                # api: 代表基于ESB/APIGW调用的接口调用
                # api.$module.$api_name
                    api.bkdata.query_data -> api/bkdata/default.py: QueryDataResource
                # resource: 基于业务逻辑的封装
                resource.plugin -> plugin/resources.py
                    resource.plugin.install_plugin -> plugin/resources.py: InstallPluginResource
                # adapter: 针对不同版本的逻辑差异进行的封装
                adapter.cc -> cc/adapter/default.py -> cc/adapter/${platform}/resources.py
                # 调用adapter.cc 即可访问对应文件下的resource，
                # 如果在${platform}/resources.py里面有相同定义，会重载default.py下的resource
        """
        setup()

        # 如果启用了API文档自动生成，则在setup完成后触发文档生成
        if API_DOCS_SETTINGS.get("ENABLED", False) and API_DOCS_SETTINGS.get(
            "AUTO_GENERATE", True
        ):
            try:
                from .documentation.generator import DocumentationGenerator

                generator = DocumentationGenerator()
                # 收集API资源信息（不生成文件，只做初始化）
                generator.collect_api_resources()
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"API文档自动生成失败: {e}")
