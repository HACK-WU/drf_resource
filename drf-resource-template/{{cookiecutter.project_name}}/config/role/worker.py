"""
Worker 角色配置
启动方式: DJANGO_ROLE=worker celery -A {{ cookiecutter.project_name }} worker -l info
"""
import os

{% if cookiecutter.enable_celery == "yes" %}
# Worker 角色仅需要 Celery + 核心模块，不需要 REST Framework / CORS / API 文档
ROOT_URLCONF = "{{ cookiecutter.project_name }}.urls"

# 精简 INSTALLED_APPS：移除 drf_resource、drf_spectacular 等 Web 专属 App
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    {% if cookiecutter.enable_celery == "yes" %}
    "django_celery_beat",
    "django_celery_results",
    {% endif %}
    "{{ cookiecutter.project_name }}.apps.example",
]

# Worker 不需要 MIDDLEWARE
MIDDLEWARE = []

# 禁用 DRF
REST_FRAMEWORK = {}

# Celery 配置（从环境变量读取，生产环境强制）
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = False
CELERYD_CONCURRENCY = int(os.getenv("CELERYD_CONCURRENCY", 2))
{% endif %}

# 定时任务调度表（参考 bk-monitor 的 DEFAULT_CRONTAB 模式）
# 格式: (task_module, cron_schedule, run_type)
# run_type: "global" 全局执行 / "cluster" 分集群执行
DEFAULT_CRONTAB = [
    # 示例：
    # ("{{ cookiecutter.project_name }}.apps.example.tasks.cleanup_expired_data", "*/30 * * * *", "global"),
]

# 耗时任务单独队列
LONG_TASK_CRONTAB = []

# 排除特定任务
EXCLUDE_WORKER_TASKS = []
