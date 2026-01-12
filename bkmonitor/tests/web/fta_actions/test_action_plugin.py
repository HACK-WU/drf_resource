"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from bkmonitor.models import ActionPlugin


class TestActionPlugin(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_get_itsm_plugin_url(self):
        ap = ActionPlugin.objects.get(id=5)
        new_info = ap.get_plugin_template_create_url()
        itsm_url = f"{settings.BK_ITSM_HOST}#/project/service/new/basic?project_id=0"
        self.assertEqual(itsm_url, new_info["url"])

    def test_get_sops_plugin_url(self):
        sops_project_mock = patch(
            "api.sops.default.GetUserProjectDetailResource.perform_request",
            MagicMock(return_value={"project_id": 2}),
        )
        sops_project_mock.start()
        ap = ActionPlugin.objects.get(id=4)
        new_info = ap.get_plugin_template_create_url(**{"bk_biz_id": 2})
        sops_url = f"{settings.BK_SOPS_HOST}template/new/2/"
        sops_project_mock.stop()
        self.assertEqual(sops_url, new_info["url"])

    def test_get_job_plugin_url(self):
        ap = ActionPlugin.objects.get(id=3)
        new_info = ap.get_plugin_template_create_url(**{"bk_biz_id": 2})
        job_url = f"{settings.JOB_URL}/2/task_manage/create"
        self.assertEqual(job_url, new_info["url"])
