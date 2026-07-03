"""REST Framework + drf_resource 配置"""
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "drf_resource.response.renderers.CustomJSONRenderer",
    ],
    "DEFAULT_EXCEPTION_HANDLER": "drf_resource.exceptions.handlers.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# drf_resource 框架配置项
DRF_RESOURCE = {}

{% if cookiecutter.enable_api_docs == "yes" %}
# API 文档 schema class
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"
{% endif %}
