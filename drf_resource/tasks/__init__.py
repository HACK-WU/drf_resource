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
异步任务模块

本模块提供了 Celery 异步任务相关功能：
    - run_perform_request: 将 Resource 作为异步任务执行
    - query_task_result: 查询任务结果
    - step: 步骤装饰器
"""

from drf_resource.tasks.celery import (
    run_perform_request,
    query_task_result,
    step,
)

__all__ = [
    "run_perform_request",
    "query_task_result",
    "step",
]
