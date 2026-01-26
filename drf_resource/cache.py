"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import functools
import json
import logging
import zlib
from collections.abc import Callable
from typing import Any

from django.core.cache import cache, caches
from django.utils.encoding import force_bytes

from drf_resource.utils.common import count_md5
from drf_resource.utils.request import get_request

logger = logging.getLogger(__name__)

try:
    mem_cache = caches["locmem"]
except Exception:
    mem_cache = cache


class CacheTypeItem:
    """
    缓存类型定义
    """

    def __init__(self, key, timeout, user_related=None, label=""):
        """
        :param key: 缓存名称
        :param timeout: 缓存超时，单位：s
        :param user_related: 是否用户相关
        :param label: 详细说明
        """
        self.key = key
        self.timeout = timeout
        self.label = label
        self.user_related = user_related

    def __call__(self, timeout):
        return CacheTypeItem(self.key, timeout, self.user_related, self.label)


class BaseCacheType:
    """
    缓存类型基类
    """

    #  user = CacheTypeItem(key="user", timeout=60 user_related=True)
    #  backend = CacheTypeItem(key="backend", timeout=60, user_related=False)
    pass


class DefaultCacheType(BaseCacheType):
    user = CacheTypeItem(key="user", timeout=60, user_related=True)
    backend = CacheTypeItem(key="backend", timeout=60, user_related=False)


class BaseUsingCache:
    """
    使用缓存基类
    """

    def __call__(self, target_fun: Callable) -> Callable:
        """
        返回经过缓存装饰的函数。
        后面
        """

        @functools.wraps(target_fun)
        def cached_wrapper(*args, **kwargs):
            return_value = self._cached(target_fun, args, kwargs)
            return return_value

        @functools.wraps(target_fun)
        def refresh_wrapper(*args, **kwargs):
            return_value = self._refresh(target_fun, args, kwargs)
            return return_value

        @functools.wraps(target_fun)
        def cacheless_wrapper(*args, **kwargs):
            return_value = self._cacheless(target_fun, args, kwargs)
            return return_value

        # 为函数设置各种调用模式
        default_wrapper = cached_wrapper
        default_wrapper.cached = cached_wrapper
        default_wrapper.refresh = refresh_wrapper
        default_wrapper.cacheless = cacheless_wrapper

        return default_wrapper

    def _cached(self, target_fun, args, kwargs):
        raise NotImplementedError

    def _refresh(self, target_fun, args, kwargs):
        raise NotImplementedError

    def _cacheless(self, target_fun, args, kwargs):
        raise NotImplementedError


class DefaultUsingCache(BaseUsingCache):
    min_length = 15
    preset = 6
    key_prefix = "web_cache"
    default_user_info = "backend"
    # 哨兵值，用于区分"缓存不存在"和"缓存的值是None"
    _CACHE_MISS = object()

    def __init__(
        self,
        cache_type: CacheTypeItem,
        backend_cache_type: CacheTypeItem | None = None,
        user_related: bool | None = None,
        compress: bool | None = True,
        cache_write_trigger: Callable[[Any], bool] = lambda res: True,
        func_key_generator: Callable[[Callable], str] | None = None,
    ) -> None:
        """
        :param cache_type: 缓存类型
        :param user_related: 是否与用户关联
        :param compress: 是否进行压缩
        :param cache_write_trigger: 缓存函数，当函数返回true时，则进行缓存
        :param func_key_generator: 函数标识key的生成逻辑
        """
        self.cache_type = cache_type
        self.backend_cache_type = backend_cache_type
        self.compress = compress
        self.cache_write_trigger = cache_write_trigger
        # 使用安全的函数key生成器，避免访问不存在的__name__属性
        self.func_key_generator = func_key_generator or self._default_func_key_generator
        # 先看用户是否提供了user_related参数
        # 若无，则查看cache_type是否提供了user_related参数
        # 若都没有定义，则user_related默认为False（大多数缓存不需要区分用户）
        if user_related is not None:
            self.user_related = user_related
        elif getattr(cache_type, "user_related", None) is not None:
            self.user_related = self.cache_type.user_related
        else:
            self.user_related = False

    def _refresh(self, target_fun: Callable, args: tuple, kwargs: dict) -> Any:
        """
        【强制刷新模式】
        不使用缓存的数据，将函数执行返回结果回写缓存
        """
        # 运行时获取缓存类型和用户信息（只获取一次）
        user_info = self.get_user_info()
        using_cache_type = self.get_using_cache_type(user_info)
        cache_key = self.generate_cache_key(
            target_fun, args, kwargs, user_info, using_cache_type
        )

        return_value = self._cacheless(target_fun, args, kwargs)

        # 设置了缓存空数据
        # 或者不缓存空数据且数据为空时
        # 需要进行缓存
        if cache_key and using_cache_type and self.cache_write_trigger(return_value):
            self.set_value(cache_key, return_value, using_cache_type.timeout)

        return return_value

    def _cacheless(self, target_fun: Callable, args: tuple, kwargs: dict) -> Any:
        """
        【忽略缓存模式】
        忽略缓存机制，直接执行函数，返回结果不回写缓存
        """
        # 执行真实函数
        return target_fun(*args, **kwargs)

    def _cached(self, target_fun: Callable, args: tuple, kwargs: dict) -> Any:
        """
        【默认缓存模式】
        先检查是否缓存是否存在
        若存在，则直接返回缓存内容
        若不存在，则执行函数，并将结果回写到缓存中
        """
        if self.is_use_cache():
            cache_key = self.generate_cache_key(target_fun, args, kwargs)
        else:
            cache_key = None

        if cache_key:
            # 使用哨兵值来区分"缓存不存在"和"缓存值是None"
            return_value = self.get_value(cache_key, default=self._CACHE_MISS)

            if return_value is self._CACHE_MISS:
                # 缓存不存在，需要刷新
                return_value = self._refresh(target_fun, args, kwargs)
        else:
            return_value = self._cacheless(target_fun, args, kwargs)
        return return_value

    # 启用缓存规则
    def is_use_cache(self) -> bool:
        """是否使用缓存"""
        return True

    @staticmethod
    def _default_func_key_generator(func: Callable) -> str:
        """
        默认的函数key生成器，安全地处理各种可调用对象。
        """
        # 优先使用 __module__ 和 __name__
        if hasattr(func, "__module__") and hasattr(func, "__name__"):
            return f"{func.__module__}.{func.__name__}"
        # 对于类实例（如Resource），使用类名
        elif hasattr(func, "__class__"):
            cls = func.__class__
            if hasattr(cls, "__module__") and hasattr(cls, "__name__"):
                return f"{cls.__module__}.{cls.__name__}"
        # 兜底：使用类型名称
        return f"{type(func).__name__}"

    def get_user_info(self) -> str:
        """
        运行时动态获取用户信息。
        每次调用时重新获取，确保在多用户场景下返回正确的用户标识。
        """
        username = self.default_user_info
        if self.user_related:
            try:
                username = get_request().user.username
            except Exception as e:
                logger.error(f"get user info error: {e}")
                username = self.default_user_info
        return username

    def get_using_cache_type(
        self, user_info: str | None = None
    ) -> CacheTypeItem | None:
        """
        根据当前用户获取适当的缓存类型。

        首先检查当前用户是否为'backend'，如果是，则根据backend_cache_type或cache_type属性确定缓存类型。
        确保返回的缓存类型是CacheTypeItem的实例，否则抛出TypeError。

        Returns:
            CacheTypeItem: 适当的缓存类型，如果未设置则为None。
        """
        # 运行时获取用户信息
        if user_info is None:
            user_info = self.get_user_info()

        # 初始缓存类型默认为实例的cache_type属性
        using_cache_type = self.cache_type

        if user_info == self.default_user_info:
            using_cache_type = self.backend_cache_type or self.cache_type

        # 检查using_cache_type是否为有效的缓存类型，如果不是则抛出异常
        if using_cache_type:
            if not isinstance(using_cache_type, CacheTypeItem):
                raise TypeError(
                    "param 'cache_type' must be an "
                    "instance of <utils.cache.CacheTypeItem>"
                )

        return using_cache_type

    def generate_cache_key(
        self,
        target_fun: Callable,
        args: tuple,
        kwargs: dict,
        user_info: str | None = None,
        using_cache_type: CacheTypeItem | None = None,
    ) -> str | None:
        """
        生成缓存key。
        运行时动态获取用户信息和缓存类型，确保每次调用生成正确的缓存key。

        :param target_fun: 目标函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :param user_info: 用户信息（可选，避免重复获取）
        :param using_cache_type: 缓存类型（可选，避免重复获取）
        """
        # 如果未提供，则运行时获取
        if user_info is None:
            user_info = self.get_user_info()
        if using_cache_type is None:
            using_cache_type = self.get_using_cache_type()

        if using_cache_type:
            return (
                f"{self.key_prefix}:{using_cache_type.key}:{self.func_key_generator(target_fun)}"
                f":{count_md5(args)}:{count_md5(kwargs)}:{user_info}"
            )

        return None

    def get_value(self, cache_key: str, default: Any = None) -> Any:
        # 先尝试从内存缓存获取
        value = mem_cache.get(cache_key, default=None)
        # 如果内存缓存没有，再从主缓存获取
        if value is None:
            value = cache.get(cache_key, default=None)

        if value is None:
            return default

        if self.compress:
            try:
                value = zlib.decompress(value)
            except (zlib.error, TypeError) as e:
                logger.warning(
                    f"Failed to decompress cache value for key {cache_key}: {e}"
                )
                return default
            try:
                value = json.loads(force_bytes(value))
            except (json.JSONDecodeError, TypeError, UnicodeDecodeError) as e:
                logger.warning(
                    f"Failed to deserialize cache value for key {cache_key}: {e}"
                )
                return default

        return value

    def set_value(self, key, value, timeout=60) -> bool:
        if self.compress:
            try:
                value = json.dumps(value)
            except Exception:
                logger.exception(f"[Cache]不支持序列化的类型: {type(value)}")
                return False

            if len(value) > self.min_length:
                value = zlib.compress(value.encode("utf-8"))  # noqa

        try:
            # 如果配置了内存缓存，则优先使用内存缓存
            # 内存缓存使用较短的超时时间（最多60秒）
            if mem_cache is not cache:
                mem_cache.set(key, value, min(timeout, 60))
            cache.set(key, value, timeout)
        except Exception as e:
            try:
                request_path = get_request().path
            except Exception:
                request_path = ""
            # 缓存出错不影响主流程
            logger.exception(
                f"存缓存[key:{key}]时报错：{e}\n value: {value!r}\nurl: {request_path}"
            )
            return False
        return True


using_cache = DefaultUsingCache
