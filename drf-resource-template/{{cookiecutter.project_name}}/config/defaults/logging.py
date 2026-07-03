"""日志配置 — 自适应：开发/容器用 console，生产用 file + console"""
import os
from config import ENVIRONMENT, BASE_DIR, PROJECT_ROOT
from config.tools.environment import IS_CONTAINER_MODE

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")

_formatters = {
    "verbose": {
        "format": "[{asctime}] {levelname} {name} {message}",
        "style": "{",
    },
}

if ENVIRONMENT == "production" and not IS_CONTAINER_MODE:
    # 生产环境（非容器）：文件 + console
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(PROJECT_ROOT, "logs", "{{ cookiecutter.project_name }}.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "formatter": "verbose",
            },
        },
        "root": {"handlers": ["console", "file"], "level": LOG_LEVEL},
        "loggers": {
            "django": {"handlers": ["console", "file"], "level": LOG_LEVEL, "propagate": False},
            "drf_resource": {"handlers": ["console", "file"], "level": LOG_LEVEL, "propagate": False},
        },
    }
else:
    # 开发/容器环境：仅 console
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {"handlers": ["console"], "level": LOG_LEVEL},
        "loggers": {
            "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
            "drf_resource": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        },
    }
