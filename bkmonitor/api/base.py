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
蓝鲸监控 API 基类

提供蓝鲸平台特定的 API 调用能力，包括：
- x-bkapi-authorization 认证头
- blueking-language 语言头
- 用户信息和凭证注入
- API 失败指标上报
- 权限中心错误处理
"""

import json
import logging
from typing import Any

from django.conf import settings
from django.utils import translation

from bkmonitor.utils.user import get_global_user, get_local_username
from core.errors.api import BKAPIError
from drf_resource.contrib.api import APICacheResource, APIResource

logger = logging.getLogger(__name__)


class BKAPIResource(APIResource):
    """
    蓝鲸 API 基类

    在通用 APIResource 基础上，添加蓝鲸平台特定功能：
    - 认证头：x-bkapi-authorization（包含 bk_app_code、bk_app_secret、bk_username）
    - 语言头：blueking-language
    - 用户信息注入：bk_username
    - 凭证注入：bk_app_code、bk_app_secret
    - 权限中心错误处理（9900403, 35999999）

    使用示例:
        class MyBKAPIResource(BKAPIResource):
            base_url = "https://bkapi.example.com"
            module_name = "my_api"
            action = "/api/v1/users/"
            method = "GET"

        result = MyBKAPIResource().request({"user_id": 123})
    """

    # 蓝鲸权限中心错误码
    BK_PERMISSION_DENIED_CODE = 9900403
    BK_PERMISSION_DENIED_CODE_V3 = 35999999

    # 是否使用 SaaS 凭证（部分 API 需要使用后台凭证）
    USE_SAAS_CREDENTIALS = False

    # bk_username 属性，可被子类覆盖
    bk_username = None

    def get_headers(self) -> dict:
        """
        获取请求头

        添加蓝鲸平台特定的认证头和语言头。
        """
        headers = super().get_headers()

        # 添加认证头
        auth_info = self._get_auth_info()
        headers["x-bkapi-authorization"] = json.dumps(auth_info)

        # 添加语言头
        language = translation.get_language()
        if language:
            headers["blueking-language"] = language

        return headers

    def _get_auth_info(self) -> dict:
        """
        获取认证信息

        返回包含 bk_app_code、bk_app_secret、bk_username 的字典。
        """
        # 获取凭证
        if self.USE_SAAS_CREDENTIALS:
            app_code = getattr(settings, "SAAS_APP_CODE", settings.APP_CODE)
            app_secret = getattr(settings, "SAAS_SECRET_KEY", settings.SECRET_KEY)
        else:
            app_code = settings.APP_CODE
            app_secret = settings.SECRET_KEY

        auth_info = {
            "bk_app_code": app_code,
            "bk_app_secret": app_secret,
        }

        # 获取用户名
        bk_username = self._get_bk_username()
        if bk_username:
            auth_info["bk_username"] = bk_username

        return auth_info

    def _get_bk_username(self) -> str:
        """
        获取 bk_username

        优先级：
        1. 实例属性 bk_username
        2. 请求中的用户名
        3. 全局用户名
        """
        # 1. 实例属性
        if self.bk_username:
            return self.bk_username

        # 2. 请求用户名
        username = get_local_username()
        if username:
            return username

        # 3. 全局用户名
        return get_global_user()

    def full_request_data(self, validated_request_data: dict) -> dict:
        """
        丰富请求数据

        注入 bk_username 到请求数据中。
        """
        validated_request_data = super().full_request_data(validated_request_data)

        # 注入用户名（某些旧 API 需要在 body 中传递）
        if "bk_username" not in validated_request_data:
            bk_username = self._get_bk_username()
            if bk_username:
                validated_request_data["bk_username"] = bk_username

        return validated_request_data

    def _handle_response(self, result: dict, validated_request_data: dict) -> Any:
        """
        处理响应结果

        在父类基础上增加权限中心错误处理。
        """
        # 检查请求是否成功
        if not result.get("result", True):
            code = result.get("code")
            message = result.get("message", "")
            data = result.get("data", {})

            # 权限中心错误特殊处理
            if code in [self.BK_PERMISSION_DENIED_CODE, self.BK_PERMISSION_DENIED_CODE_V3]:
                self._handle_permission_denied(code, message, data)

            # 上报失败指标
            self.report_api_failure_metric(code, message)

            raise BKAPIError(
                system_name=self.module_name,
                url=self.action,
                result={
                    "code": code,
                    "message": message,
                },
            )

        # 获取数据
        response_data = result.get("data")

        # 渲染响应数据
        return self.render_response_data(validated_request_data, response_data)

    def _handle_permission_denied(self, code: int, message: str, data: dict):
        """
        处理权限中心拒绝错误

        子类可覆盖以实现自定义的权限处理逻辑。
        """
        # 记录权限拒绝日志
        logger.warning(
            f"[{self.module_name}] Permission denied: code={code}, message={message}, "
            f"action={self.action}, permission_data={data}"
        )

    def report_api_failure_metric(self, code: int, message: str):
        """
        上报 API 失败指标

        子类可覆盖以实现自定义的指标上报逻辑。
        """
        try:
            from bkmonitor.utils.metric import Metric

            Metric.push(
                "api_failure_total",
                {
                    "module": self.module_name,
                    "action": self.action,
                    "code": str(code),
                },
            )
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Report API failure metric error: {e}")

    def on_request_error(self, request_id: str, error: Exception) -> None:
        """
        请求错误钩子

        上报错误指标。
        """
        super().on_request_error(request_id, error)

        # 上报失败指标
        self.report_api_failure_metric(-1, str(error))


class BKAPICacheResource(BKAPIResource, APICacheResource):
    """
    带缓存的蓝鲸 API 基类

    继承关系：
        - BKAPIResource: 提供蓝鲸特定的认证和错误处理
        - APICacheResource: 提供缓存功能

    使用示例:
        from drf_resource.cache import CacheTypeItem

        class CachedBKAPIResource(BKAPICacheResource):
            base_url = "https://bkapi.example.com"
            module_name = "my_api"
            action = "/api/v1/users/"
            method = "GET"

            cache_type = CacheTypeItem(timeout=60)

        result = CachedBKAPIResource().request({"user_id": 123})
    """

    def __init__(self, context=None):
        """
        初始化

        需要正确处理多重继承的初始化顺序。
        """
        # 先检查是否需要缓存包装
        need_cache = self._need_cache_wrap()

        # 初始化 BKAPIResource
        BKAPIResource.__init__(self, context=context)

        # 如果需要缓存，包装 request 方法
        if need_cache:
            self._wrap_request()
