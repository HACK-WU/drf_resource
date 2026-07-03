# S-01：脚手架引擎设计

> 父文档：[DESIGN.md](DESIGN.md) | 共享术语：cruft、功能开关、条件渲染

## 术语

| 术语 | 定义 |
|------|------|
| cookiecutter.json | 模板变量定义文件，声明所有用户可配置参数及 choices |
| pre_gen_project.py | 生成前钩子，校验用户输入的变量是否合法 |
| post_gen_project.py | 生成后钩子，输出下一步操作指引并清理条件未启用的文件 |

## 现状（AS-IS）

- bk-resource 的 `cookiecutter.json` 仅 3 个变量（app_id, project_name, python_version），无功能开关
- 无 pre_gen/post_gen hooks，不校验变量也不引导用户

## 方案（TO-BE）

### 1. cookiecutter.json — 模板变量定义

文件：[`cookiecutter.json`](file:///drf-resource-template/cookiecutter.json)（模板仓库根目录）

```json
{
    "project_name": "my_project",
    "project_description": "A Django REST Framework project powered by drf_resource",
    "author_name": "Your Name",
    "python_version": ["3.11", "3.12", "3.13"],
    "database_backend": ["sqlite", "mysql", "postgresql"],
    "enable_celery": ["yes", "no"],
    "enable_redis_cache": ["yes", "no"],
    "enable_cors": ["yes", "no"],
    "enable_i18n": ["yes", "no"],
    "enable_api_docs": ["yes", "no"],
    "_copy_without_render": [
        "static",
        "*.css",
        "*.js"
    ]
}
```

**变量设计决策**：

| 决策 | 选定方案 | 被否决方案 | 否决理由 |
|------|---------|-----------|---------|
| 项目名约束 | 仅允许 `[a-z][a-z0-9_]*` | 允许任意字符串 | Python 包名必须是合法标识符 |
| 变量风格 | `["yes", "no"]` choices | `true`/`false` 布尔值 | cookiecutter 对布尔值支持不完善 |
| 数据库选项 | sqlite/mysql/postgresql | 仅 sqlite | 生产环境需要 MySQL/PG |
| Python 版本 | 3.11+ | 3.8+ | drf_resource 要求 Python >= 3.11 |

### 2. hooks/pre_gen_project.py — 变量校验

文件：[`hooks/pre_gen_project.py`](file:///drf-resource-template/hooks/pre_gen_project.py)

```python
"""模板变量校验 - 生成前执行"""
import re
import sys

PROJECT_NAME = "{{ cookiecutter.project_name }}"

# 校验项目名格式
if not re.match(r'^[a-z][a-z0-9_]*$', PROJECT_NAME):
    print(f"ERROR: '{PROJECT_NAME}' 不是合法的 Python 包名。")
    print("项目名只能包含小写字母、数字和下划线，且必须以字母开头。")
    print("例如: my_project, demo_app, api_service")
    sys.exit(1)

# 校验项目名不与保留字冲突
RESERVED = {"config", "apps", "tests", "manage", "django", "rest_framework"}
if PROJECT_NAME in RESERVED:
    print(f"ERROR: '{PROJECT_NAME}' 是保留名称，请换一个名称。")
    sys.exit(1)

print(f"✅ 项目名 '{PROJECT_NAME}' 校验通过")
```

### 3. hooks/post_gen_project.py — 生成后引导

文件：[`hooks/post_gen_project.py`](file:///drf-resource-template/hooks/post_gen_project.py)

```python
"""生成后引导 - 输出下一步操作"""
import os

PROJECT_NAME = "{{ cookiecutter.project_name }}"
ENABLE_CELERY = "{{ cookiecutter.enable_celery }}" == "yes"

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

4. 配置环境变量（可选）：
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
""")

# 清理不需要的文件
{% if cookiecutter.enable_celery == "no" %}
for f in ["{{ cookiecutter.project_name }}/celery.py"]:
    if os.path.exists(f):
        os.remove(f)
{% endif %}
```

## 异常处理

| 场景 | 行为 | 对外暴露 |
|------|------|---------|
| cookiecutter 变量校验失败（项目名不合法） | 输出错误信息并 `sys.exit(1)` | 是，控制台输出 |
| cookiecutter 变量校验失败（保留名称冲突） | 同上 | 是，控制台输出 |
| cruft update 冲突 | cruft 自带冲突检测，提示手动合并 | 是，控制台输出 |
