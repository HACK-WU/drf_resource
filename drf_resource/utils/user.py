"""
用户信息工具模块

提供用户信息的获取、设置和管理功能，支持多种场景：
- Web 请求场景：从 request 对象获取用户信息
- Celery 任务场景：从线程局部变量获取用户信息
- 后台任务场景：从配置获取默认用户信息
"""

from django.conf import settings
from drf_resource.utils.local import local
from drf_resource.utils.request import get_request


def get_request_user():
    """
    获取请求中的用户对象
    :return: 用户对象，若无法获取则返回 None
    """
    request = get_request(peaceful=True)
    if request:
        return request.user


def get_request_username(default=""):
    """
    基于 request 获取用户名（Web 场景）

    尝试从当前请求对象获取用户名，如果失败则从线程局部变量获取，
    最后返回默认值。

    :param default: 获取失败时的默认返回值
    :return: 用户名字符串
    """
    try:
        username = get_request().user.username
    except Exception:
        try:
            username = local.username
        except Exception:
            username = default
    return username


def get_local_username():
    """
    从 local 对象中获取用户信息（Celery 场景）

    按优先级依次尝试从 bk_username、username、operator 三个属性获取用户名。

    :return: 用户名字符串，若无法获取则返回 None
    """
    for user_key in ["bk_username", "username", "operator"]:
        username = getattr(local, user_key, None)
        if username is not None:
            return username


def get_backend_username():
    """
    从配置中获取后台用户名

    :return: 配置中的 COMMON_USERNAME，若未配置则返回 None
    """
    return getattr(settings, "COMMON_USERNAME", None)


def set_local_username(username):
    """
    设置线程局部用户名

    :param username: 要设置的用户名
    """
    local.username = username


def set_request_username(username):
    """
    设置请求中的用户名

    如果当前有请求对象，则设置请求对象的用户名；
    否则设置线程局部变量中的用户名。

    :param username: 要设置的用户名
    """
    request = get_request(peaceful=True)
    if request:
        # 有请求对象，就设置请求对象
        request.user.username = username
    else:
        # 没有请求对象，就设置local
        local.username = username


def get_global_user(peaceful=True) -> str:
    """
    获取全局用户名

    按以下优先级获取用户名：
    1. 从当前请求对象获取
    2. 从线程局部变量获取
    3. 从配置中获取后台用户名

    :param peaceful: 若为 False 且无法获取用户名，则抛出异常
    :return: 用户名字符串
    :raises ValueError: 当 peaceful=False 且无法获取用户名时抛出
    """
    username = get_request_username() or get_local_username() or get_backend_username()

    if username:
        return username

    if not peaceful:
        raise ValueError("get_global_user: 无法获取用户信息")

    return ""


def make_userinfo():
    """
    生成用户信息字典

    :return: 包含 bk_username 的用户信息字典
    :raises ValueError: 当无法获取用户信息时抛出
    """
    username = get_global_user()
    if username:
        return {"bk_username": username}

    raise ValueError("make_userinfo: 获取用户信息失败")
