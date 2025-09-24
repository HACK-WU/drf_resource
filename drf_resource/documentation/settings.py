# -*- coding: utf-8 -*-
"""
API文档配置设置

该模块定义API文档生成的配置参数。
"""

from django.conf import settings

# API文档默认配置
API_DOCS_DEFAULT_SETTINGS = {
    # 是否启用API文档功能
    "ENABLED": getattr(settings, "DEBUG", False),
    # 文档标题
    "TITLE": "DRF Resource API Documentation",
    # 文档版本
    "VERSION": "1.0.0",
    # 文档描述
    "DESCRIPTION": "Auto-generated API documentation for DRF Resource framework",
    # 文档输出目录
    "OUTPUT_DIR": (getattr(settings, "STATIC_ROOT", None) or "static") + "/api_docs/",
    # 文档访问URL前缀
    "URL_PREFIX": "/api-docs/",
    # 是否自动生成文档
    "AUTO_GENERATE": True,
    # 是否启用交互式测试
    "ENABLE_TESTING": True,
    # 支持的认证方式
    "AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # 权限类
    "PERMISSION_CLASSES": [],
    # 是否需要登录
    "REQUIRE_LOGIN": False,
    # 文档主题配色
    "THEME": {
        "primary_color": "#1890ff",
        "success_color": "#52c41a",
        "warning_color": "#faad14",
        "error_color": "#f5222d",
    },
    # 过滤设置
    "FILTERS": {
        # 隐藏的模块列表
        "HIDDEN_MODULES": [],
        # 隐藏的API类别
        "HIDDEN_CATEGORIES": [],
        # 只显示的标签
        "INCLUDE_TAGS": [],
        # 排除的标签
        "EXCLUDE_TAGS": [],
    },
    # OpenAPI设置
    "OPENAPI": {
        "VERSION": "3.0.3",
        "SERVERS": [],
        "SECURITY_SCHEMES": {
            "BKAPIAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "x-bkapi-authorization",
                "description": "BlueKing API Gateway认证",
            }
        },
    },
    # 模板设置
    "TEMPLATES": {
        "ENGINE": "jinja2",
        "DIRS": [],
        "OPTIONS": {
            "autoescape": True,
        },
    },
    # 缓存设置
    "CACHE": {
        "ENABLED": True,
        "TIMEOUT": 3600,  # 1小时
        "KEY_PREFIX": "api_docs",
    },
    # 日志设置
    "LOGGING": {
        "LEVEL": "INFO",
        "HANDLER": "console",
    },
}


def get_api_docs_setting(key, default=None):
    """
    获取API文档配置

    Args:
        key: 配置键
        default: 默认值

    Returns:
        配置值
    """
    user_settings = getattr(settings, "API_DOCS_SETTINGS", {})
    return user_settings.get(key, API_DOCS_DEFAULT_SETTINGS.get(key, default))


def get_all_api_docs_settings():
    """
    获取所有API文档配置

    Returns:
        Dict: 完整的配置字典
    """
    user_settings = getattr(settings, "API_DOCS_SETTINGS", {})
    final_settings = API_DOCS_DEFAULT_SETTINGS.copy()
    final_settings.update(user_settings)
    return final_settings


# 导出配置对象
API_DOCS_SETTINGS = get_all_api_docs_settings()
