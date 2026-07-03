"""生成后引导 - 输出下一步操作"""
import os

PROJECT_NAME = "{{ cookiecutter.project_name }}"
ENABLE_CELERY = "{{ cookiecutter.enable_celery }}" == "yes"
ENABLE_REDIS_CACHE = "{{ cookiecutter.enable_redis_cache }}" == "yes"
ENABLE_CORS = "{{ cookiecutter.enable_cors }}" == "yes"
ENABLE_I18N = "{{ cookiecutter.enable_i18n }}" == "yes"
ENABLE_API_DOCS = "{{ cookiecutter.enable_api_docs }}" == "yes"

print(f"""
✅ 项目 {PROJECT_NAME} 已生成！

📋 接下来的步骤：

1. 进入项目目录：
   cd {PROJECT_NAME}

2. 创建虚拟环境：
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\\Scripts\\activate   # Windows

3. 安装依赖：
   pip install -r requirements.txt

4. 配置环境变量：
   cp .env.example .env
   # 编辑 .env 文件配置数据库等

5. 初始化数据库：
   python manage.py migrate

6. 启动开发服务器：
   python manage.py runserver
""")

if ENABLE_CELERY:
    print("""
🔧 Celery 已启用，启动 worker：
   celery -A {{ cookiecutter.project_name }} worker -l info
   # 启动 beat（定时任务）：
   celery -A {{ cookiecutter.project_name }} beat -l info
""")

if ENABLE_REDIS_CACHE:
    print("""
📦 Redis 缓存已启用，请确保 Redis 服务可用：
   redis-server  # 或通过 Docker 启动
""")

if ENABLE_API_DOCS:
    print("""
📚 API 文档已启用：
   访问 http://localhost:8000/api/docs/ 查看 Swagger UI
""")

# 清理不需要的文件
import shutil
{% if cookiecutter.enable_celery == "no" %}
# 删除 Celery 相关文件
shutil.rmtree("config/celery", ignore_errors=True)
{% endif %}
