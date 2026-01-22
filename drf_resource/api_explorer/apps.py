from django.apps import AppConfig


class ApiExplorerConfig(AppConfig):
    """API Explorer Django 应用配置"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_resource.api_explorer"
    verbose_name = "API Explorer"

    def ready(self):
        """应用就绪时的初始化操作"""
        pass
