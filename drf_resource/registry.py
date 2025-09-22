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
import abc
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Type

import inflection

logger = logging.getLogger(__name__)


class ResourceRegistry:
    """
    全局资源注册表，负责管理所有已注册的资源
    """

    def __init__(self):
        # 存储注册的资源信息
        # 格式: {(module_path, name): registration_info}
        self._registry: Dict[tuple, Dict[str, Any]] = {}
        # 存储已创建的 ResourceShortcut 实例
        self._shortcuts: Dict[str, Any] = {}
        # 是否已同步到 ResourceManager
        self._synced = False

    def register_resource(
        self, name: str, resource_class: Type, module_path: str = None, custom_name: bool = False
    ) -> None:
        """
        注册资源类

        Args:
            name: 资源名称
            resource_class: 资源类
            module_path: 模块路径
            custom_name: 是否为自定义名称
        """
        if module_path is None:
            module_path = self._infer_module_path(resource_class)

        key = (module_path, name)

        # 检查是否已存在同名资源
        if key in self._registry:
            existing = self._registry[key]
            logger.exception(
                f"Resource '{name}' already registered in module '{module_path}'. "
                f"Existing: {existing['resource_object']}, "
                f"New: {resource_class}"
            )
            raise ValueError(f"Resource '{name}' already registered in module '{module_path}'")

        # 注册资源信息
        registration_info = {
            'name': name,
            'resource_type': 'class',
            'resource_object': resource_class,
            'module_path': module_path,
            'register_time': datetime.now(),
            'custom_name': custom_name,
        }

        self._registry[key] = registration_info

        logger.debug(f"Registered resource: {module_path}.{name} -> {resource_class}")

        # 如果已经同步过，需要更新 ResourceManager
        if self._synced:
            self._update_manager_for_resource(module_path, name, resource_class)

    def register_function(
        self, name: str, function: callable, module_path: str = None, custom_name: bool = False
    ) -> None:
        """
        注册函数资源

        Args:
            name: 函数名称
            function: 函数对象
            module_path: 模块路径
            custom_name: 是否为自定义名称
        """
        if module_path is None:
            module_path = function.__module__

        key = (module_path, name)

        # 检查是否已存在同名资源
        if key in self._registry:
            logger.warning(f"Function '{name}' already registered in module '{module_path}'")
            return

        # 注册函数信息
        registration_info = {
            'name': name,
            'resource_type': 'function',
            'resource_object': function,
            'module_path': module_path,
            'register_time': datetime.now(),
            'custom_name': custom_name,
        }

        self._registry[key] = registration_info

        logger.debug(f"Registered function: {module_path}.{name} -> {function}")

        # 如果已经同步过，需要更新 ResourceManager
        if self._synced:
            self._update_manager_for_function(module_path, name, function)

    def unregister(self, name: str, module_path: str) -> bool:
        """
        注销资源

        Args:
            name: 资源名称
            module_path: 模块路径

        Returns:
            bool: 是否成功注销
        """
        key = (module_path, name)
        if key in self._registry:
            del self._registry[key]
            logger.debug(f"Unregistered resource: {module_path}.{name}")
            return True
        return False

    def get_resource(self, name: str, module_path: str) -> Optional[Dict[str, Any]]:
        """
        获取资源信息

        Args:
            name: 资源名称
            module_path: 模块路径

        Returns:
            Optional[Dict]: 资源信息或 None
        """
        key = (module_path, name)
        return self._registry.get(key)

    def list_resources(self, module_path: str = None) -> Dict[str, Dict[str, Any]]:
        """
        列出资源

        Args:
            module_path: 可选的模块路径过滤

        Returns:
            Dict: 资源信息字典
        """
        if module_path is None:
            return {f"{mp}.{name}": info for (mp, name), info in self._registry.items()}
        else:
            return {name: info for (mp, name), info in self._registry.items() if mp == module_path}

    def sync_to_manager(self) -> None:
        """
        同步注册表到 ResourceManager
        保持与现有调用方式的兼容性
        """

        # 按模块路径分组资源
        module_groups = {}
        for (module_path, name), info in self._registry.items():
            if module_path not in module_groups:
                module_groups[module_path] = {}
            module_groups[module_path][name] = info

        # 为每个模块创建 ResourceShortcut
        for module_path, resources in module_groups.items():
            self._create_resource_shortcut(module_path, resources)

        self._synced = True
        logger.debug("Resource registry synced to ResourceManager")

    def clear_legacy(self) -> None:
        """
        清理旧的文件扫描机制相关代码
        这个方法会在移除旧机制时调用
        """
        # 标记为已清理，实际的代码移除在其他地方进行
        logger.debug("Legacy file scanning mechanism marked for removal")

    def _infer_module_path(self, resource_class: Type) -> str:
        """
        推导模块路径

        Args:
            resource_class: 资源类

        Returns:
            str: 推导的模块路径
        """
        module_name = resource_class.__module__
        module_name = module_name.split(".")
        # 被注册的类必须定义在resources包下或其子包下,或者是在default包下
        if "resources" not in module_name and "default" not in module_name:
            if "api" not in module_name:
                raise ValueError(f"Resource class {resource_class.__name__} must be defined in resources package")
            else:
                raise ValueError(f"Resource class {resource_class.__name__} must be defined in default package")

        # 将resources或者default的上一层作为模块路径返回
        if "resources" in module_name:
            module_name = ".".join(module_name[: module_name.index("resources")])
        elif "default" in module_name:
            module_name = ".".join(module_name[: module_name.index("default")])

        return module_name

    def _infer_resource_name(self, resource_class: Type) -> str:
        """
        推导资源名称

        Args:
            resource_class: 资源类

        Returns:
            str: 推导的资源名称
        """
        class_name = resource_class.__name__

        # 移除常见的后缀
        if class_name.endswith('Resource'):
            cleaned_name = class_name[:-8]  # 移除 'Resource'
        elif class_name.endswith('API'):
            cleaned_name = class_name[:-3] + '_api'  # 'API' -> '_api'
        else:
            cleaned_name = class_name

        # 转换为下划线格式
        return inflection.underscore(cleaned_name)

    def _create_resource_shortcut(self, module_path: str, resources: Dict[str, Dict[str, Any]]) -> None:
        """
        为模块创建 ResourceShortcut

        Args:
            module_path: 模块路径
            resources: 该模块的资源字典
        """
        from drf_resource.management.root import (
            adapter,
            api,
            is_adapter,
            is_api,
            resource,
        )

        # 创建虚拟的 ResourceShortcut 实例
        class DynamicResourceShortcut:
            def __init__(self, module_path: str, resources: Dict[str, Dict[str, Any]]):
                self._path = module_path
                self._methods = {}
                self.loaded = True

                # 注册所有资源
                for name, info in resources.items():
                    resource_obj = info['resource_object']
                    if info['resource_type'] == 'class':
                        # 为类创建实例
                        setattr(self, name, resource_obj())
                        self._methods[name] = resource_obj
                    else:
                        # 直接绑定函数
                        setattr(self, name, resource_obj)
                        self._methods[name] = resource_obj

            def list_method(self):
                return list(self._methods.keys())

            def reload_method(self, method, func):
                setattr(self, method, func)
                self._methods[method] = func

        # 创建资源快捷方式实例
        shortcut = DynamicResourceShortcut(module_path, resources)

        # 确定注册到哪个根管理器
        root_manager = resource
        # module_path 示例: monitor_web.strategy.alert
        shortcut_name = module_path.split('.')[-1]

        if is_api(module_path):
            root_manager = api
        elif is_adapter(module_path):
            root_manager = adapter

        # 注册到相应的根管理器
        # 支持快捷调用：resource.alert
        setattr(root_manager, shortcut_name, shortcut)
        # 支持完整路径调用：resource.monitor_web.strategy.alert
        setattr(root_manager, module_path, shortcut)

        # 保存快捷方式引用
        self._shortcuts[module_path] = shortcut

    def _update_manager_for_resource(self, module_path: str, name: str, resource_class: Type) -> None:
        """
        为新注册的资源更新管理器
        """
        if module_path in self._shortcuts:
            shortcut = self._shortcuts[module_path]
            # 创建资源实例并添加到快捷方式
            setattr(shortcut, name, resource_class())
            shortcut._methods[name] = resource_class

    def _update_manager_for_function(self, module_path: str, name: str, function: callable) -> None:
        """
        为新注册的函数更新管理器
        """
        if module_path in self._shortcuts:
            shortcut = self._shortcuts[module_path]
            # 直接添加函数到快捷方式
            setattr(shortcut, name, function)
            shortcut._methods[name] = function


# 全局注册表实例
resource_registry = ResourceRegistry()


class ResourceMeta(abc.ABCMeta):
    """
    Resource 元类，用于自动注册继承 Resource 的类
    继承自 abc.ABCMeta 以保持与现有抽象类的兼容性
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        # 创建类
        cls = super().__new__(mcs, name, bases, namespace)

        # 检查是否需要自动注册
        auto_register = getattr(cls, 'auto_register', True)
        if not auto_register:
            return cls

        # 避免注册 Resource 基类本身
        if name == 'Resource' and len(bases) == 1:
            return cls

        # 过滤抽象类：检查是否有未实现的抽象方法
        # 如果类有抽象方法，说明它是抽象类，不应该被注册用于实例化
        if getattr(cls, "__abstractmethods__", None):
            return cls

        # 如果当前类不是直接继承自 Resource，检查是否在继承链中
        if not (hasattr(cls, '__mro__') and any(base.__name__ == 'Resource' for base in cls.__mro__[1:])):
            return cls

        # 获取注册名称
        register_name = getattr(cls, 'register_name', None)
        if register_name is None:
            register_name = resource_registry._infer_resource_name(cls)

        # 获取注册模块路径
        register_module = getattr(cls, 'register_module', None)
        if register_module is None:
            register_module = resource_registry._infer_module_path(cls)

        # 注册资源
        custom_name = hasattr(cls, 'register_name')
        resource_registry.register_resource(
            name=register_name, resource_class=cls, module_path=register_module, custom_name=custom_name
        )

        return cls


def get_registry() -> ResourceRegistry:
    """
    获取全局注册表实例

    Returns:
        ResourceRegistry: 全局注册表实例
    """
    return resource_registry
