# -*- coding: utf-8 -*-
"""
API文档生成模块

该模块负责为DRF Resource框架自动生成API文档，集成drf-spectacular库
并提供自定义的文档生成功能。
"""

from .extensions import APIResourceExtension
from .generator import DocumentationGenerator
from .schema import APIResourceSchema
from .settings import API_DOCS_SETTINGS

__all__ = [
    "DocumentationGenerator",
    "APIResourceExtension",
    "APIResourceSchema",
    "API_DOCS_SETTINGS",
]
