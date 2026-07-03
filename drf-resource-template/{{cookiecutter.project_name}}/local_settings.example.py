"""
本地开发覆盖配置
==================
使用方法：
    cp local_settings.example.py local_settings.py
    # 编辑 local_settings.py 覆盖个人开发配置

此文件仅作为模板，local_settings.py 被 .gitignore 忽略。
"""

# DEBUG = True
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": "/tmp/dev.db",
#     }
# }
{% if cookiecutter.enable_celery == "yes" %}
# CELERY_TASK_ALWAYS_EAGER = True  # 同步执行 Celery 任务（调试用）
{% endif %}
# LOG_LEVEL = "DEBUG"
