# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## 快速开始

### 环境要求

- Python {{ cookiecutter.python_version }}+
- {% if cookiecutter.database_backend == "mysql" %}MySQL 5.7+{% elif cookiecutter.database_backend == "postgresql" %}PostgreSQL 12+{% else %}无额外依赖（SQLite）{% endif %}
{% if cookiecutter.enable_redis_cache == "yes" %}- Redis 6.0+{% endif %}

### 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd {{ cookiecutter.project_name }}

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env

# 初始化数据库
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

访问 http://localhost:8000/api/ 查看 API。
{% if cookiecutter.enable_api_docs == "yes" %}
访问 http://localhost:8000/api/docs/ 查看 API 文档。
{% endif %}

## 项目结构

```
{{ cookiecutter.project_name }}/
├── manage.py
├── config/          # 配置目录
├── apps/            # 业务 App
└── tests/           # 测试
```

## 技术栈

- Django + DRF + drf_resource
{% if cookiecutter.enable_celery == "yes" %}- Celery（异步任务）
{% endif %}
{% if cookiecutter.enable_redis_cache == "yes" %}- Redis（缓存）
{% endif %}
