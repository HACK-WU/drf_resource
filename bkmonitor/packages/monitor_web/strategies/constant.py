"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from bkmonitor.models import AlgorithmModel
from constants.data_source import DataSourceLabel, DataTypeLabel


class Scenario:
    UPTIME_CHECK = "uptimecheck"
    HOST = "HOST"
    SERVICE = "SERVICE"


# 检测算法判断值为int的键
DETECT_ALGORITHM_INT_LIST = ["count", "ceil_interval", "floor_interval", "days"]

DETECT_ALGORITHM_METHOD_LIST = ["eq", "gt", "gte", "lte", "lt", "neq"]

# 检测算法判断为float的键
DETECT_ALGORITHM_FLOAT_OR_INT_LIST = ["ceil", "floor", "threshold", "shock", "ratio"]

DETECT_ALGORITHM_CHOICES = [
    "",
    AlgorithmModel.AlgorithmChoices.Threshold,
    AlgorithmModel.AlgorithmChoices.PartialNodes,
    AlgorithmModel.AlgorithmChoices.SimpleRingRatio,
    AlgorithmModel.AlgorithmChoices.AdvancedRingRatio,
    AlgorithmModel.AlgorithmChoices.SimpleYearRound,
    AlgorithmModel.AlgorithmChoices.AdvancedYearRound,
    AlgorithmModel.AlgorithmChoices.OsRestart,
    AlgorithmModel.AlgorithmChoices.ProcPort,
    AlgorithmModel.AlgorithmChoices.YearRoundAmplitude,
    AlgorithmModel.AlgorithmChoices.YearRoundRange,
    AlgorithmModel.AlgorithmChoices.RingRatioAmplitude,
    AlgorithmModel.AlgorithmChoices.PingUnreachable,
    AlgorithmModel.AlgorithmChoices.IntelligentDetect,
]

# 默认触发条件配置
GLOBAL_TRIGGER_CONFIG = {"check_window": 5, "count": 1}

# 默认告警触发条件配置
DEFAULT_TRIGGER_CONFIG_MAP = {
    DataSourceLabel.BK_MONITOR_COLLECTOR: {
        DataTypeLabel.TIME_SERIES: {
            "system.cpu_summary.usage": {"check_window": 5, "count": 3},
            "system.io.util": {"check_window": 5, "count": 3},
        },
        DataTypeLabel.EVENT: {
            "system.event.agent-gse": {"check_window": 10, "count": 1},
            "system.event.disk-readonly-gse": {"check_window": 10, "count": 1},
            "system.event.ping-gse": {"check_window": 5, "count": 3},
        },
    }
}

# 原table_id存入extend_filed字段名
ORIGIN_RESULT_TABLE_ID = "origin_result_table_id"

# 标签其他
OTHER_RT_LABEL = "other_rt"
# 内置标签
BASE_LABEL_LIST = [
    "os",
    "host_process",
    "service_process",
    "component",
    "service_module",
    "uptimecheck",
    "application_check",
    "host_device",
    "hardware_device",
]

# os_restart、proc_port、ping-gse对应的item的metric_id
EVENT_METRIC_ID = [
    "bk_monitor.os_restart",
    "bk_monitor.proc_port",
    "bk_monitor.ping-gse",
    "bk_monitor.gse_process_event",
]


# 告警变量,告警变量,进程变量
class ValueableList:
    VALUEABLELIST = [
        {
            "id": "CMDB_VAR",
            "name": _lazy("CMDB变量"),
            "description": {
                "format": _lazy("{{target.对象.字段名}}"),
                "object": [
                    {"id": "business", "name": _lazy("业务")},
                    {"id": "host", "name": _lazy("主机")},
                    {"id": "process", "name": _lazy("进程")},
                    {"id": "service", "name": _lazy("服务实例")},
                ],
                "field": _lazy("CMDB中定义的字段名"),
            },
            "items": [
                {"id": "target.business.bk_biz_id", "name": _lazy("业务ID"), "description": "2"},
                {"id": "target.business.bk_biz_name", "name": _lazy("业务名称"), "description": _lazy("蓝鲸")},
                {
                    "id": "target.business.bk_biz_developer_string",
                    "name": _lazy("开发人员字符串"),
                    "description": "admin,user1,user2",
                },
                {
                    "id": "target.business.bk_biz_maintainer_string",
                    "name": _lazy("运维人员字符串"),
                    "description": "admin,user1",
                },
                {"id": "target.business.bk_biz_tester_string", "name": _lazy("测试人员字符串"), "description": "admin,user1"},
                {
                    "id": "target.business.bk_biz_productor_string",
                    "name": _lazy("产品人员字符串"),
                    "description": "admin,user1",
                },
                {"id": "target.business.operator_string", "name": _lazy("操作人员字符串"), "description": "admin,user1"},
                {"id": "target.host.module_string", "name": _lazy("模块名"), "description": "module1,module2"},
                {"id": "target.host.set_string", "name": _lazy("集群名"), "description": "set1,set2"},
                {"id": "target.host.bk_host_id", "name": _lazy("主机ID"), "description": "1"},
                {"id": "target.host.bk_cloud_id", "name": _lazy("云区域ID"), "description": "0"},
                {"id": "target.host.bk_cloud_name", "name": _lazy("云区域名称"), "description": _lazy("默认区域")},
                {"id": "target.host.bk_host_innerip", "name": _lazy("内网IP"), "description": "127.0.0.1"},
                {"id": "target.host.bk_host_outerip", "name": _lazy("外网IP"), "description": "127.0.1.11"},
                {"id": "target.host.bk_host_name", "name": _lazy("主机名"), "description": ""},
                {"id": "target.host.bk_os_name", "name": _lazy("操作系统名称"), "description": "linux"},
                {"id": "target.host.bk_os_type", "name": _lazy("操作系统类型(枚举数值)"), "description": "1"},
                {"id": "target.host.operator_string", "name": _lazy("负责人"), "description": "admin,user1"},
                {"id": "target.host.bk_bak_operator_string", "name": _lazy("备份负责人"), "description": "admin,user1"},
                {"id": "target.host.bk_comment", "name": _lazy("备注信息"), "description": "comment"},
                {"id": "target.host.bk_host_name", "name": _lazy("主机名"), "description": "VM_1,VM_2"},
                {"id": "target.host.bk_host_innerip", "name": _lazy("内网IP"), "description": "127.0.0.1,127.0.0.2"},
                {"id": "target.service_instance.service_instance_id", "name": _lazy("服务实例ID"), "description": "1"},
                {"id": "target.service_instance.name", "name": _lazy("服务实例名"), "description": "xxx_127.0.1.11"},
                {"id": "target.service_instances.service_instance_id", "name": _lazy("服务实例ID"), "description": "1,2"},
                {
                    "id": "target.service_instances.name",
                    "name": _lazy("服务实例名"),
                    "description": "xxx_127.0.1.11,xxx_127.0.1.12",
                },
                {"id": "target.processes[0].port", "name": _lazy("第i个进程的端口"), "description": "80"},
                {"id": 'target.process["process_name"].bk_process_id', "name": _lazy("进程ID"), "description": "1"},
                {
                    "id": 'target.process["process_name"].bk_process_name',
                    "name": _lazy("进程名称"),
                    "description": _lazy("进程1"),
                },
                {"id": 'target.process["process_name"].bk_func_name', "name": _lazy("进程功能名称"), "description": "java"},
                {"id": 'target.process["process_name"].bind_ip', "name": _lazy("绑定IP"), "description": "127.0.1.10"},
                {"id": 'target.process["process_name"].port', "name": _lazy("绑定端口"), "description": "1,2,3-5,7-10"},
            ],
        },
        {
            "id": "ALARM_VAR",
            "name": _lazy("告警变量"),
            "description": {"format": "{{a.b}}", "object": None, "field": None},
            "items": [
                {"id": 'alarm.dimensions["dimension_name"].display_name', "name": _lazy("维度名"), "description": "目标IP"},
                {
                    "id": 'alarm.dimensions["dimension_name"].display_value',
                    "name": _lazy("维度值"),
                    "description": "127.0.0.1",
                },
                {"id": "alarm.target_string", "name": _lazy("告警目标"), "description": "127.0.1.10,127.0.1.11"},
                {"id": "alarm.dimension_string", "name": _lazy("告警维度(除目标)"), "description": _lazy("磁盘=C,主机名=xxx")},
                {"id": "alarm.collect_count", "name": _lazy("汇总事件数量"), "description": "10"},
                {"id": "alarm.notice_from", "name": _lazy("消息来源"), "description": _lazy("蓝鲸监控")},
                {"id": "alarm.company", "name": _lazy("企业标识"), "description": _lazy("蓝鲸")},
                {"id": "alarm.data_source_name", "name": _lazy("数据来源名称"), "description": _lazy("计算平台")},
                {"id": "alarm.data_source", "name": _lazy("数据来源"), "description": "BKMONITOR"},
                {"id": "alarm.detail_url", "name": _lazy("详情链接"), "description": ""},
                {"id": "alarm.current_value", "name": _lazy("当前值"), "description": "1.1"},
                {"id": "alarm.target_type", "name": _lazy("目标类型"), "description": "IP/INSTANCE/TOPO"},
                {"id": "alarm.target_type_name", "name": _lazy("目标类型名称"), "description": _lazy("IP/实例/节点")},
            ],
        },
        {
            "id": "STRATEGY_VAR",
            "name": _lazy("策略变量"),
            "description": {"format": "{{a.b}}", "object": None, "field": None},
            "items": [
                {"id": "strategy.strategy_id", "name": _lazy("策略ID"), "description": "1"},
                {"id": "strategy.name", "name": _lazy("策略名称"), "description": _lazy("CPU总使用率")},
                {"id": "strategy.scenario", "name": _lazy("场景"), "description": "os"},
                {"id": "strategy.source_type", "name": _lazy("数据来源"), "description": "BKMONITOR"},
                {"id": "strategy.bk_biz_id", "name": _lazy("业务ID"), "description": "2"},
                {"id": "strategy.item.result_table_id", "name": _lazy("结果表名称"), "description": "system.cpu_detail"},
                {"id": "strategy.item.name", "name": _lazy("指标名称"), "description": _lazy("空闲率")},
                {"id": "strategy.item.metric_field", "name": _lazy("指标字段"), "description": "idle"},
                {"id": "strategy.item.unit", "name": _lazy("单位"), "description": "%"},
                {"id": "strategy.item.agg_interval", "name": _lazy("周期"), "description": "60"},
                {"id": "strategy.item.agg_method", "name": _lazy("聚合方法"), "description": "AVG"},
            ],
        },
        {
            "id": "CONTENT_VAR",
            "name": _lazy("内容变量"),
            "description": {"format": "{{a.b}}", "object": None, "field": None},
            "items": [
                {"id": "content.level", "name": _lazy("告警级别"), "description": ""},
                {"id": "content.time", "name": _lazy("最近异常时间"), "description": ""},
                {"id": "content.duration", "name": _lazy("告警持续时间"), "description": ""},
                {"id": "content.target_type", "name": _lazy("告警目标类型"), "description": ""},
                {"id": "content.data_source", "name": _lazy("告警数据来源"), "description": ""},
                {"id": "content.content", "name": _lazy("告警内容"), "description": ""},
                {"id": "content.biz", "name": _lazy("告警业务"), "description": ""},
                {"id": "content.target", "name": _lazy("告警目标"), "description": ""},
                {"id": "content.dimension", "name": _lazy("告警维度"), "description": ""},
                {"id": "content.detail", "name": _lazy("告警详情"), "description": ""},
                {"id": "content.related_info", "name": _lazy("关联信息"), "description": ""},
                {"id": "content.begin_time", "name": _lazy("首次异常时间"), "description": ""},
            ],
        },
    ]


# corefile signal维度的枚举值
CORE_FILE_SIGNAL_LIST = [
    "SIGQUIT",
    "SIGILL",
    "SIGTRAP",
    "SIGABRT",
    "SIGIOT",
    "SIGBUS",
    "SIGFPE",
    "SIGSEGV",
    "SIGXCPU",
    "SIGXFSZ",
    "SIGSYS",
    "SIGUNUSED",
]

# K8S系统内置标签
K8S_BUILTIN_LABEL = _("k8s_系统内置")

# 默认告警策略的加载类型
DEFAULT_ALARM_STRATEGY_LOADER_TYPE_OS = "os"
DEFAULT_ALARM_STRATEGY_LOADER_TYPE_GSE = "gse"
DEFAULT_ALARM_STRATEGY_LOADER_TYPE_K8S = "k8s"

# 默认告警策略的配置属性名
DEFAULT_ALARM_STRATEGY_ATTR_NAME_OS = "DEFAULT_OS_STRATEGIES"
DEFAULT_ALARM_STRATEGY_ATTR_NAME_GSE = "DEFAULT_GSE_PROCESS_EVENT_STRATEGIES"
DEFAULT_ALARM_STRATEGY_ATTR_NAME_K8S = "DEFAULT_K8S_STRATEGIES"
