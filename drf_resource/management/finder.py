"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# API 模块目录名，用于区分 API 资源和普通资源
# todo 支持在drf_resource中配置
API_DIR = "api"


class ResourceStatus(Enum):
    """资源加载状态"""

    UNLOADED = "unloaded"  # 未加载
    LOADED = "loaded"  # 已加载
    ERROR = "error"  # 加载失败
    IGNORED = "ignored"  # 被忽略


@dataclass
class ResourcePath:
    """
    资源路径信息类

    用于表示发现的资源模块路径及其加载状态。

    Attributes:
        path: 资源的点分隔路径 (如 "app.resources")
        status: 资源加载状态
    """

    path: str
    status: ResourceStatus = field(default=ResourceStatus.UNLOADED)

    def loaded(self):
        """标记资源为已加载"""
        self.status = ResourceStatus.LOADED

    def error(self):
        """标记资源加载失败"""
        self.status = ResourceStatus.ERROR

    def ignored(self):
        """标记资源被忽略"""
        self.status = ResourceStatus.IGNORED

    def __repr__(self):
        return f"{self.path}: {self.status.value}"


class ResourceFinder:
    """
    资源发现器

    用于在项目中自动发现 Resource 模块。支持以下目录结构：
    - resources.py: 单文件资源模块
    - resources/: 资源包目录
    - adapter/default.py: 适配器模块
    - api/{module}/default.py: API 资源模块

    Example:
        finder = ResourceFinder()
        for path in finder.resource_path:
            print(path)  # 输出: app.resources: unloaded
    """

    # 资源模块入口文件/目录名
    RESOURCE_ENTRIES = ("resources.py", "resources")
    # 适配器模块入口
    ADAPTER_ENTRY = os.path.join("adapter", "default.py")
    # API 模块入口
    API_ENTRY = "default.py"

    def __init__(self, base_dirs: list[str] | None = None):
        """
        初始化资源发现器

        Args:
            base_dirs: 基础目录列表，默认使用 Django INSTALLED_APPS 中的应用目录
        """
        self._resource_paths: list[ResourcePath] = []
        self._base_dirs = base_dirs or self._get_app_dirs()
        self._discover()

    def _get_app_dirs(self) -> list[str]:
        """获取 INSTALLED_APPS 中的应用目录"""
        app_dirs = []
        for app in getattr(settings, "INSTALLED_APPS", []):
            # 跳过 Django 内置应用和第三方应用
            if app.startswith("django.") or "." not in app:
                try:
                    # 尝试获取应用的路径
                    from importlib import import_module

                    module = import_module(app)
                    if hasattr(module, "__path__"):
                        app_dirs.extend(module.__path__)
                    elif hasattr(module, "__file__") and module.__file__:
                        app_dirs.append(os.path.dirname(module.__file__))
                except ImportError:
                    continue
            else:
                # 对于点分隔的应用名，取第一部分作为基础目录
                base_app = app.split(".")[0]
                try:
                    from importlib import import_module

                    module = import_module(base_app)
                    if hasattr(module, "__path__"):
                        for path in module.__path__:
                            if path not in app_dirs:
                                app_dirs.append(path)
                except ImportError:
                    continue

        # 添加项目根目录
        base_dir = getattr(settings, "BASE_DIR", None)
        if base_dir and base_dir not in app_dirs:
            app_dirs.append(str(base_dir))

        return app_dirs

    def _discover(self):
        """发现所有资源模块"""
        discovered = set()

        for base_dir in self._base_dirs:
            base_path = Path(base_dir)
            if not base_path.exists():
                continue

            # 发现普通资源模块
            self._discover_resources(base_path, discovered)

            # 发现适配器模块
            self._discover_adapters(base_path, discovered)

            # 发现 API 模块
            self._discover_api(base_path, discovered)

    def _discover_resources(self, base_path: Path, discovered: set):
        """发现普通资源模块"""
        for entry in self.RESOURCE_ENTRIES:
            for path in base_path.rglob(entry):
                # 跳过 adapter 目录下的资源
                if "adapter" in path.parts:
                    continue
                # 跳过 API 目录下的资源
                if API_DIR in path.parts:
                    continue

                dotted_path = self._path_to_dotted(path, base_path)
                if dotted_path and dotted_path not in discovered:
                    discovered.add(dotted_path)
                    self._resource_paths.append(ResourcePath(dotted_path))

    def _discover_adapters(self, base_path: Path, discovered: set):
        """发现适配器模块"""
        for path in base_path.rglob(self.ADAPTER_ENTRY):
            dotted_path = self._path_to_dotted(path, base_path)
            if dotted_path and dotted_path not in discovered:
                discovered.add(dotted_path)
                self._resource_paths.append(ResourcePath(dotted_path))

        # 发现平台特定的适配器
        platform = getattr(settings, "PLATFORM", None)
        if platform:
            platform_adapter = os.path.join("adapter", platform, "resources.py")
            for path in base_path.rglob(platform_adapter):
                dotted_path = self._path_to_dotted(path, base_path)
                if dotted_path and dotted_path not in discovered:
                    discovered.add(dotted_path)
                    self._resource_paths.append(ResourcePath(dotted_path))

    def _discover_api(self, base_path: Path, discovered: set):
        """发现 API 模块"""
        api_path = base_path / API_DIR
        if not api_path.exists():
            return

        for path in api_path.rglob(self.API_ENTRY):
            dotted_path = self._path_to_dotted(path, base_path)
            if dotted_path and dotted_path not in discovered:
                discovered.add(dotted_path)
                self._resource_paths.append(ResourcePath(dotted_path))

    def _path_to_dotted(self, path: Path, base_path: Path) -> str | None:
        """将文件路径转换为点分隔的模块路径"""
        try:
            # 获取相对路径
            rel_path = path.relative_to(base_path)

            # 移除文件后缀
            if path.is_file():
                rel_path = rel_path.with_suffix("")

            # 转换为点分隔格式
            parts = rel_path.parts

            # 如果以 __init__ 结尾，移除它
            if parts and parts[-1] == "__init__":
                parts = parts[:-1]

            if not parts:
                return None

            return ".".join(parts)
        except ValueError:
            return None

    @property
    def resource_path(self) -> list[ResourcePath]:
        """获取所有发现的资源路径"""
        return self._resource_paths

    def __iter__(self):
        return iter(self._resource_paths)

    def __len__(self):
        return len(self._resource_paths)
