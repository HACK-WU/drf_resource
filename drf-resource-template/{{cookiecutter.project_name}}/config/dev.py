"""开发环境配置"""
DEBUG = True
ALLOWED_HOSTS = ["*"]

# 开发环境使用简单静态资源
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

{% if cookiecutter.enable_celery == "yes" %}
# 开发环境 Celery 同步执行（调试用）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
{% endif %}
