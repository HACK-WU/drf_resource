"""功能模块汇总导入 — settings.py 第 2 步通过 `from config.defaults import *` 加载"""
# 加载顺序约束：apps 必须最先，env_override 必须最后

# 1. Django 核心（必须最先加载）
from config.defaults.apps import *  # noqa
# 2. 数据库
from config.defaults.database import *  # noqa
# 3. 缓存
from config.defaults.cache import *  # noqa
# 4. REST Framework
from config.defaults.rest_framework import *  # noqa
# 5. 静态资源
from config.defaults.static_files import *  # noqa
# 6. Session
from config.defaults.session import *  # noqa
# 7. 日志
from config.defaults.logging import *  # noqa

{% if cookiecutter.enable_celery == "yes" %}
# 8. Celery（条件生成）
from config.defaults.celery import *  # noqa
{% endif %}
{% if cookiecutter.enable_cors == "yes" %}
# 9. CORS（条件生成）
from config.defaults.cors import *  # noqa
{% endif %}
{% if cookiecutter.enable_i18n == "yes" %}
# 10. 国际化（条件生成）
from config.defaults.i18n import *  # noqa
{% endif %}
{% if cookiecutter.enable_api_docs == "yes" %}
# 11. API 文档（条件生成）
from config.defaults.api_docs import *  # noqa
{% endif %}

# 12. 环境变量覆盖（必须最后加载，可覆盖前面所有配置）
from config.defaults.env_override import *  # noqa
