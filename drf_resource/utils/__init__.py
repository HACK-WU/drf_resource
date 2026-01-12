# -*- coding: utf-8 -*-
"""
drf_resource 工具模块

导出常用的工具函数和类。
"""

# 通用工具
from drf_resource.utils.common import ErrorDetails, count_md5, failed

# 本地存储
from drf_resource.utils.local import (
    Local,
    get_ident,
    local,
    with_client_operator,
    with_client_user,
    with_request_local,
)

# 请求工具
from drf_resource.utils.request import get_request

# 文本处理工具
from drf_resource.utils.text import camel_to_underscore, underscore_to_camel

# 线程后端工具
from drf_resource.utils.thread_backend import (
    InheritParentThread,
    ThreadPool,
    ignored,
    run_func_with_local,
    run_threads,
)

# 用户信息工具
from drf_resource.utils.user import (
    get_backend_username,
    get_global_user,
    get_local_username,
    get_request_user,
    get_request_username,
    make_userinfo,
    set_local_username,
    set_request_username,
)

__all__ = [
    # 用户信息工具
    "get_request_username",
    "get_local_username",
    "get_backend_username",
    "get_global_user",
    "get_request_user",
    "set_local_username",
    "set_request_username",
    "make_userinfo",
    # 线程后端工具
    "ThreadPool",
    "InheritParentThread",
    "run_threads",
    "run_func_with_local",
    "ignored",
    # 文本处理工具
    "camel_to_underscore",
    "underscore_to_camel",
    # 通用工具
    "count_md5",
    "failed",
    "ErrorDetails",
    # 本地存储
    "local",
    "Local",
    "get_ident",
    "with_request_local",
    "with_client_user",
    "with_client_operator",
    # 请求工具
    "get_request",
]
