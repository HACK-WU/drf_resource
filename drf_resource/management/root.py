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
import inspect
import logging
import os
from contextlib import contextmanager
from importlib import import_module

import inflection
from drf_resource.base import Resource
from drf_resource.management.exceptions import (
    ResourceModuleConflict,
    ResourceModuleNotRegistered,
    ResourceNotRegistered,
)
from drf_resource.registry import resource_registry

logger = logging.getLogger(__name__)

# 判断是否DRFResource是否已经初始化
__setup__ = False


@contextmanager
def _lazy_load(_instance):
    # _instance就是ResourceShortcut实例，确保_resource_module_instance._setup()方法被调用
    if not _instance.loaded:
        getattr(_instance, "_setup", lambda: None)()
    yield _instance


def lazy_load(func):
    def wrapper(resource_module_instance, *args, **kwargs):
        with _lazy_load(resource_module_instance):
            return func(resource_module_instance, *args, **kwargs)

    return wrapper


class ResourceShortcut(object):
    _package_pool = {}

    # 定义Resource模块的入口名称，resources指的就是resources.py或者resources包
    _entry = "resources"

    def __new__(cls, module_path: str):
        def init_instance(self, m_path):
            # 确保module_path 以 resources 结尾
            if not m_path.endswith(self._entry):
                m_path += ".{}".format(self._entry)
            # resource模块所在目录的路径
            self._path = m_path
            # resource模块所在包
            self._package = None
            # Resource类转为下划线字符串后，保存在self._methods中
            # {"get_info_info":GetInfoResource}
            self._methods = {}
            self.loaded = False
            # 新增单元测试 patch 支持
            self.__deleted_methods = {}

        if module_path not in cls._package_pool:
            instance = object.__new__(cls)
            init_instance(instance, module_path)
            cls._package_pool[module_path] = instance
        return cls._package_pool[module_path]

    def __init__(self, module_path):
        # init in __new__ function
        pass

    def __getitem__(self, x):
        # delete _entry(replace once from right)
        path = "".join(self._path.rsplit(self._entry, 1)).strip(".")
        dotted_path = path.split(".")
        if not isinstance(x, slice):
            return dotted_path[x]
        rm = resource
        while dotted_path[:-1]:
            rm = getattr(rm, dotted_path.pop(0))
        return tuple(rm)

    def _setup(self):
        """
        私有方法，用于动态设置资源。

        本方法尝试导入指定路径下的模块，并自动检测模块中的资源类和函数。
        对于每个检测到的资源类（非抽象且继承自Resource的类），创建一个实例并作为当前实例的属性。
        对于每个函数，直接绑定为当前实例的属性。
        此方法在内部使用，主要用于初始化和动态加载资源。
        """
        try:
            # 尝试导入指定路径下的模块
            self._package = import_module(self._path)
        except ImportError as e:
            # 如果导入失败，抛出ImportError异常，提供详细的错误信息
            raise ImportError("resource called before {} setup. detail: {}".format(self._path, e))

        # 遍历模块中的所有属性和方法
        for name, obj in list(self._package.__dict__.items()):
            # 忽略以"_"开头的私有属性和方法
            if name.startswith("_"):
                continue

            # 忽略抽象类
            if inspect.isabstract(obj):
                continue

            # 如果是继承自Resource的类，创建一个实例并作为当前实例的属性
            if inspect.isclass(obj) and issubclass(obj, Resource):
                # 移除类名中的"Resource"后缀，如果存在的话
                cleaned_name = "".join(name.rsplit("Resource", 1)) if name.endswith("Resource") else name
                # 将类名转换为下划线风格，用作属性名
                property_name = camel_to_underscore(cleaned_name)
                setattr(self, property_name, obj())
                self._methods[property_name] = obj

            # 同时支持将函数直接绑定为当前实例的属性
            if inspect.isfunction(obj):
                setattr(self, name, obj)
                self._methods[name] = obj

        # 标记资源为已加载
        self.loaded = True

    def __delattr__(self, name):
        if name in self._methods:
            self.__deleted_methods[name] = self._methods.pop(name)
        super(ResourceShortcut, self).__delattr__(name)

    @lazy_load
    def __getattr__(self, item):
        if item in self._methods:
            return getattr(self, item)
        try:
            if item.endswith(self._entry):
                # 支持导入当前ResourceShortcut对应路径下的子模块，并将其转为ResourceShortcut实例
                return ResourceShortcut(import_module("{}.{}".format(self._path, item)).__name__)
            else:
                # 支持导入当前ResourceShortcut对应路径下的子模块
                return import_module("{}.{}".format(self._path, item))
        except ImportError:
            if item in self.__deleted_methods:
                return self.__deleted_methods[item]
            raise ResourceNotRegistered("Resource {} not in [{}]".format(item, self._package.__name__))

    @lazy_load
    def list_method(self):
        return list(self._methods.keys())

    def reload_method(self, method, func):
        setattr(self, method, func)
        self._methods[method] = func


class AdapterResourceShortcut(ResourceShortcut):
    _entry = "adapter.default"
    _package_pool = {}


class APIResourceShortcut(ResourceShortcut):
    _entry = "default"
    _package_pool = {}


class ResourceManager(tuple):
    """
    ResourceManager 类继承自 tuple，用于管理资源的层级结构。
    它允许动态添加子资源，并维护资源间的父子关系。
    底层使用 tuple 作为底层数据结构。

    新功能：
    - 支持快捷调用方式：resource.alert
    - 支持完整路径调用方式：resource.monitor_web.strategy.alert
    - 自动创建中间层级节点
    - 路径冲突检测和错误处理
    """

    __parent__ = None  # 父资源引用，用于维护资源层级关系

    def __contains__(self, item):
        """
        重写 __contains__ 方法，用于检查项是否是资源本身或以资源为前缀。

        参数:
        - item: 需要检查的项

        返回:
        - bool: 项是否是资源本身或以资源为前缀
        """
        return item is not None and (self is item or item[: len(self)] == self)

    def __getattr__(self, name):
        """
        重写 __getattr__ 方法，用于动态添加或获取子资源。
        如果是设置阶段，优先检查直接设置的属性，然后尝试从转换后的对象中获取属性。
        如果未找到则抛出异常。否则，创建新的 ResourceManager 实例作为子资源。

        参数:
        - name: 属性名

        返回:
        - ResourceManager 或其他类型: 动态添加的子资源或获取的属性值
        """
        # 快捷方式挂载完成后，优先检查直接设置的属性
        if __setup__:
            # 先检查是否有直接设置的属性（通过 setattr_with_path 设置的）
            if hasattr(super(ResourceManager, self), name):
                return super(ResourceManager, self).__getattribute__(name)

            # 如果没有直接设置的属性，尝试从转换后的对象中获取
            transform_result = self.transform()
            if transform_result is not None:
                got = getattr(transform_result, name, None)
                if got is not None:
                    return got

            # 如果都没找到，抛出异常
            raise ResourceModuleNotRegistered('module: "%s" is not registered, maybe not in `INSTALLED_APPS` ?' % name)

        # 创建新的子资源实例,并将当当前self的内容添加到子资源中。
        # 然后给当前self(这个元组)添加name属性，指向新创建的子资源。
        # 假设name是"a",那么self.a=("a",)
        new = ResourceManager(self + (name,))
        setattr(self, name, new)
        new.__parent__ = self
        return new

    def __repr__(self):
        """
        重写 __repr__ 方法，返回资源的字符串表示。

        返回:
        - str: 资源的字符串表示
        """
        # self本身是一个元组对象，当self为空时，返回"resource"
        # 当self不为空时，返回"resource."+ self中的内容，以"."分隔.
        # 比如当self的内容为("a", "b", "c")时，返回"resource.a.b.c"
        return "resource" + ("." if self else "") + ".".join(self)

    def __bool__(self):
        """
        重写 __bool__ 方法，根据资源长度返回布尔值。

        返回:
        - bool: 资源是否非空
        """
        return bool(len(self))

    @property
    def __root__(self):
        """
        获取资源树的根节点。

        返回:
        - ResourceManager: 资源树的根节点
        """
        target = self
        while target.__parent__ is not None:
            target = target.__parent__
        return target

    def transform(self):
        """
        获取到当前资源的最尾端的资源。

        返回:
        - Callable or None: 转换后的可调用对象或 None
        """
        func_finder = self.__root__
        # self本身是一个元组对象self[0]的值就是当前的资源名称
        # 循环self中的值，获取到当前resource的最后一个子资源的实例，然后从实例中获取属性
        for attr in self:
            func_finder = getattr(func_finder, attr)

        # 获取到的func_finder如果是ResourceManager实例，说明资源未注册，返回None。
        if isinstance(func_finder, self.__class__):
            return None
            # raise Exception("func called before resource setup."
            #                 " detail: %s" % str(self))

        return func_finder

    def __call__(self, *args, **kwargs):
        """
        重写 __call__ 方法，使 ResourceManager 实例可调用。
        调用转换后的对象，并传递参数。

        参数:
        - *args: 位置参数
        - **kwargs: 关键字参数

        返回:
        - Any: 调用结果
        """
        return self.transform()(*args, **kwargs)

    def setattr_with_path(self, name: str, value) -> None:
        """
        支持包含点号的完整路径属性设置。
        这个方法可以处理两种注册方式：
        1. 快捷调用方式：resource.alert
        2. 完整路径调用方式：resource.monitor_web.strategy.alert

        参数:
        - name: 属性名，可能包含点号的完整路径
        - value: 要设置的值，通常是 ResourceShortcut 实例

        抛出:
        - ResourceModuleConflict: 当路径冲突时
        - ValueError: 当路径格式不正确时
        """
        if not name or not isinstance(name, str):
            raise ValueError("Attribute name must be a non-empty string")

        # 如果名称不包含点号，直接设置
        if '.' not in name:
            # 检查冲突
            if hasattr(self, name):
                existing_attr = getattr(self, name)
                # 如果已存在同名的 ResourceShortcut，抛出冲突异常
                if hasattr(existing_attr, '_path'):
                    raise ResourceModuleConflict(
                        f"Resource conflict: '{name}' already exists with path '{existing_attr._path}'"
                    )

            # 直接设置属性
            object.__setattr__(self, name, value)
            return

        # 处理包含点号的完整路径
        path_segments = name.split('.')
        current_manager = self

        # 遍历路径段，除了最后一个
        for segment in path_segments[:-1]:
            if not segment:  # 跳过空段
                continue

            # 检查是否已存在该段
            if hasattr(current_manager, segment):
                next_manager = getattr(current_manager, segment)
                # 如果已经是 ResourceShortcut，不能再创建子节点
                if hasattr(next_manager, '_path'):
                    raise ResourceModuleConflict(
                        f"Cannot create path '{name}': segment '{segment}' is already a ResourceShortcut"
                    )
                # 如果不是 ResourceManager，也不能继续
                if not isinstance(next_manager, ResourceManager):
                    raise ValueError(f"Cannot create path '{name}': segment '{segment}' is not a ResourceManager")
                current_manager = next_manager
            else:
                # 创建新的中间节点
                new_manager = ResourceManager(current_manager + (segment,))
                object.__setattr__(current_manager, segment, new_manager)
                new_manager.__parent__ = current_manager
                current_manager = new_manager

        # 设置最后一个段的值
        final_segment = path_segments[-1]
        if not final_segment:
            raise ValueError(f"Invalid path '{name}': cannot end with a dot")

        # 检查最终段的冲突
        if hasattr(current_manager, final_segment):
            existing_attr = getattr(current_manager, final_segment)
            if hasattr(existing_attr, '_path'):
                raise ResourceModuleConflict(f"Resource conflict: '{final_segment}' already exists at path '{name}'")

        # 设置最终值
        object.__setattr__(current_manager, final_segment, value)


def setup():
    """
    初始化新的自动注册机制
    替代原有的文件扫描机制，通过元类和装饰器实现自动注册
    """
    global __setup__
    if __setup__:
        return

    # 同步注册表到 ResourceManager
    resource_registry.sync_to_manager()

    __setup__ = True

    # 清理旧的机制引用
    resource_registry.clear_legacy()


def is_api(dotted_path):
    """
    【已废弃】判断是否为API路径
    新机制通过模块路径自动识别
    """
    return 'api' in dotted_path.split('.')


def is_adapter(dotted_path):
    """
    【已废弃】判断是否为适配器路径
    新机制通过模块路径自动识别
    """
    return "adapter" in dotted_path.split(".")


# ============================================================================
# 已废弃的工具函数，保留用于向后兼容
# ============================================================================


def path_to_dotted(path) -> str:
    """
    【已废弃】将文件路径转换为带点的字符串格式
    新机制不再依赖文件路径转换
    """
    return ".".join([p for p in path.split(os.sep) if p])


def camel_to_underscore(camel_str):
    """
    【保留】将驼峰式字符串转换为下划线格式
    这个函数仍然被新的命名推导机制使用
    """
    return inflection.underscore(camel_str)


resource = ResourceManager()

adapter = ResourceManager()

api = ResourceManager()
