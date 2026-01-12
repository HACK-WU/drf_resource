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

"""
简化的监控指标模块，避免依赖 bkmonitor
"""

import logging

logger = logging.getLogger(__name__)


class DummyMetric:
    """虚拟指标类，用于替代 Prometheus 指标"""

    def __init__(self, name, description="", labelnames=None):
        self.name = name
        self.description = description
        self.labelnames = labelnames or []

    def labels(self, **kwargs):
        """返回自身以支持链式调用"""
        return self

    def inc(self, amount=1):
        """增加计数（空实现）"""
        pass


class DummyMetrics:
    """虚拟监控指标管理类"""

    # API 失败请求总数
    API_FAILED_REQUESTS_TOTAL = DummyMetric(
        "api_failed_requests_total",
        "API failed requests total",
        labelnames=["action", "module", "code", "role", "exception", "user_name"],
    )

    @staticmethod
    def report_all():
        """上报所有指标（空实现）"""
        pass


# 导出实例
metrics = DummyMetrics()
