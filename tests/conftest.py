"""
tests 目录的 pytest conftest
在导入其他模块之前配置 Django
"""

import os
import sys

# 添加 httpflex 到 Python 路径
httpflex_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "httpflex-py", "src"
)
if httpflex_path not in sys.path:
    sys.path.insert(0, httpflex_path)

# 清除环境变量，避免 .env 文件干扰
os.environ.pop("DJANGO_SETTINGS_MODULE", None)
os.environ.pop("DJANGO_CONF_MODULE", None)

# 在任何其他导入之前配置 Django
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key",
        ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "rest_framework",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        REST_FRAMEWORK={
            "TEST_REQUEST_DEFAULT_FORMAT": "json",
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        },
        BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        API_DIR="api",
        PLATFORM="community",
        ROLE="web",
        APP_CODE="test_app",
        DRF_RESOURCE={
            "API_EXPLORER_ENABLED": True,
        },
    )
    django.setup()
