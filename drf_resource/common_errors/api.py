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
API请求错误
"""

from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from drf_resource.common_errors import Error


class APIError(Error):
    """
    API 请求错误（通用）

    用于表示 HTTP API 请求过程中发生的错误，包括：
    - 网络超时
    - HTTP 错误状态码
    - 业务逻辑错误

    参数:
        system_name: 系统/模块名称
        url: 请求的 URL 或端点
        result: 错误结果，可以是字符串或包含 code/message 的字典
    """

    code = 3301001
    name = _lazy("API请求错误")

    def __init__(self, system_name: str = "", url: str = "", result=None):
        """
        初始化 API 错误

        :param system_name: 系统/模块名称
        :param url: 请求的 URL 或端点
        :param result: 错误消息或包含错误信息的字典
        """
        message_tpl = _("请求系统'{system_name}'错误，")
        if not isinstance(result, dict):
            result = {"message": result}
        if result.get("code") is not None:
            message_tpl += _("返回错误码: {code}，")
        message_tpl += _("返回消息: {message}，")
        message_tpl += _("请求URL: {url}")

        self.data = result
        self.message = message_tpl.format(
            system_name=system_name,
            code=result.get("code"),
            url=url,
            message=result.get("message") or _("空"),
        )
        # 设置返回错误详情信息，适配新版错误样式
        self.set_details(
            exc_type=type(self).__name__,
            exc_code=result.get("code") or self.code,
            overview=_("请求系统'{system_name}'错误，").format(system_name=system_name),
            detail=result.get("message"),
            popup_message="warning",
        )


# 保留别名以兼容旧代码
BKAPIError = APIError


class DevopsNotDeployedError(APIError):
    """
    蓝盾环境未部署错误
    """

    code = 3301002
    name = _lazy("蓝盾环境未部署")
