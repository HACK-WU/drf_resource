"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

"""
通用工具函数模块，避免依赖 bkmonitor
"""


def get_bk_login_ticket(request):
    """
    从 request 中获取用户登录凭据

    这是一个简化版本，避免依赖 blueapps
    """
    # 简化实现：尝试从常见位置获取登录票据
    ticket_keys = ["bk_ticket", "bk_token", "ticket", "token"]

    # 1. 从 COOKIES 中获取
    for key in ticket_keys:
        value = request.COOKIES.get(key)
        if value:
            return {key: value}

    # 2. 从 GET 参数中获取
    for key in ticket_keys:
        value = request.GET.get(key)
        if value:
            return {key: value}

    # 3. 从 META 中获取
    for key in ticket_keys:
        meta_key = f"HTTP_{key.upper()}"
        value = request.META.get(meta_key)
        if value:
            return {key: value}

    return {}
