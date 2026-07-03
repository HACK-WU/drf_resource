"""
Django settings 入口

加载顺序（6 步）：
    1. config/__init__.py  → 基础常量
    2. config/defaults/     → 功能模块
    3. config/role/{role}.py → 角色差异
    4. config/{env}.py      → 环境差异
    5. 环境变量覆盖          → SETTINGS_ 前缀自动注入
    6. local_settings.py    → 开发环境个人覆盖
"""
import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
DJANGO_ROLE = os.getenv("DJANGO_ROLE", "web")

ENV_MODULE_MAP = {
    "development": "dev",
    "testing": "stag",
    "production": "prod",
}

# 1. 基础常量
from config import *  # noqa

# 2. 功能模块
from config.defaults import *  # noqa

# 3. 角色差异
_role_module = f"config.role.{DJANGO_ROLE}"
try:
    _role = __import__(_role_module, globals(), locals(), ["*"])
    for _s in dir(_role):
        if _s.isupper():
            locals()[_s] = getattr(_role, _s)
except ImportError:
    raise ImportError(f"无法导入角色配置 '{_role_module}'，请检查 DJANGO_ROLE 环境变量")

# 4. 环境差异
_env = ENV_MODULE_MAP.get(DJANGO_ENV, "dev")
_env_module = f"config.{_env}"
try:
    _module = __import__(_env_module, globals(), locals(), ["*"])
    for _s in dir(_module):
        if _s.isupper():
            locals()[_s] = getattr(_module, _s)
except ImportError as e:
    raise ImportError(f"无法导入环境配置 '{_env_module}': {e}")

# 5. 环境变量覆盖（config/defaults/env_override.py 已加载，此处省略）

# 6. local_settings.py 覆盖
if DJANGO_ENV == "development":
    try:
        from local_settings import *  # noqa
    except ImportError:
        pass

{% if cookiecutter.database_backend == "mysql" %}
# MySQL 兼容（Django 4.2+）
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
{% endif %}
