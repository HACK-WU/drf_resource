# S-04：功能开关与可选依赖设计

> 父文档：[DESIGN.md](DESIGN.md) | 共享术语：功能开关、条件渲染

## 术语

| 术语 | 定义 |
|------|------|
| 功能开关 | cookiecutter 变量控制模板是否包含某功能（如 enable_celery） |
| 条件渲染 | Jinja2 `{% if cookiecutter.enable_xxx %}` 决定是否生成某段代码 |
| _copy_without_render | cookiecutter 特殊变量，指定的文件不渲染（原样复制） |

## 现状（AS-IS）

bk-resource 的模板仅有 3 个 cookiecutter 变量（app_id, project_name, python_version），无功能开关机制，所有功能全量生成。

## 方案（TO-BE）

### 条件渲染矩阵

| 功能开关 | 影响的文件 | 条件渲染内容 |
|---------|-----------|-------------|
| `enable_celery` | `config/__init__.py`, `defaults/__init__.py`, `defaults/celery.py`, `defaults/apps.py`, `role/worker.py`, `config/celery/`（整个包）, `requirements.txt`, `pyproject.toml`, `manage.py`, `.env.example` | Celery app 导入、INSTALLED_APPS、broker 配置、celery 依赖、gevent patch、celery 环境变量 |
| `enable_redis_cache` | `defaults/cache.py`, `role/web.py`, `.env.example`, `requirements.txt`, `pyproject.toml` | Redis cache 配置、Session backend 切换、Redis 环境变量、django-redis 依赖 |
| `enable_cors` | `defaults/__init__.py`, `defaults/cors.py`, `defaults/apps.py`, `requirements.txt`, `pyproject.toml` | CorsMiddleware、CORS 配置、django-cors-headers 依赖 |
| `enable_i18n` | `defaults/__init__.py`, `defaults/i18n.py`, `defaults/apps.py`, `requirements.txt` | LocaleMiddleware、LOCALE_PATHS、LANGUAGES |
| `enable_api_docs` | `defaults/__init__.py`, `defaults/api_docs.py`, `defaults/rest_framework.py`, `urls.py`, `requirements.txt`, `pyproject.toml` | drf-spectacular 配置、schema/docs 端点、drf-spectacular 依赖 |
| `database_backend` | `defaults/database.py`, `settings.py`, `config/tools/mysql.py`, `.env.example`, `requirements.txt`, `pyproject.toml` | 数据库引擎配置、PyMySQL/psycopg2 依赖、MySQL 辅助函数、DB 环境变量 |

### requirements.txt — 条件渲染

文件：[`{{cookiecutter.project_name}}/requirements.txt`](file:///requirements.txt)

```text
# 核心依赖
Django{% if cookiecutter.python_version == "3.13" %}>=5.0{% else %}>=4.2{% endif %}
djangorestframework>=3.14
drf-resource>=0.1.0
whitenoise>=6.0
python-dotenv>=1.0

# 数据库
{% if cookiecutter.database_backend == "mysql" %}
pymysql>=1.0
{% elif cookiecutter.database_backend == "postgresql" %}
psycopg2-binary>=2.9
{% endif %}

# 可选依赖
{% if cookiecutter.enable_celery == "yes" %}
celery>=5.0
django-celery-beat>=2.5
django-celery-results>=2.5
{% endif %}
{% if cookiecutter.enable_redis_cache == "yes" %}
django-redis>=5.0
redis>=4.0
{% endif %}
{% if cookiecutter.enable_cors == "yes" %}
django-cors-headers>=4.0
{% endif %}
{% if cookiecutter.enable_api_docs == "yes" %}
drf-spectacular>=0.27
{% endif %}
```

### pyproject.toml — 条件渲染

文件：[`{{cookiecutter.project_name}}/pyproject.toml`](file:///pyproject.toml)

参考 drf_resource 和 bk-monitor 的 pyproject.toml，提供完整的 PEP-621 元数据 + ruff/pytest/coverage 配置：

```toml
[build-system]
build-backend = "setuptools.build_meta"
requires = ["setuptools>=61", "wheel"]

[project]
name = "{{ cookiecutter.project_name }}"
version = "0.1.0"
description = "{{ cookiecutter.project_description }}"
readme = "README.md"
requires-python = ">={{ cookiecutter.python_version }}"
{% if cookiecutter.author_name %}
authors = [{ name = "{{ cookiecutter.author_name }}" }]
{% endif %}
license = { text = "MIT" }
keywords = ["django", "drf", "rest-framework", "drf-resource"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "Framework :: Django :: 4.2",
    "Framework :: Django :: 5.0",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    "Django>=4.2",
    "djangorestframework>=3.14",
    "drf-resource>=0.1.0",
    "whitenoise>=6.0",
    "python-dotenv>=1.0",
    {% if cookiecutter.database_backend == "mysql" %}"pymysql>=1.0",
    {% elif cookiecutter.database_backend == "postgresql" %}"psycopg2-binary>=2.9",
    {% endif %}
    {% if cookiecutter.enable_celery == "yes" %}"celery>=5.0",
    "django-celery-beat>=2.5",
    "django-celery-results>=2.5",
    {% endif %}
    {% if cookiecutter.enable_redis_cache == "yes" %}"django-redis>=5.0",
    "redis>=4.0",
    {% endif %}
    {% if cookiecutter.enable_cors == "yes" %}"django-cors-headers>=4.0",
    {% endif %}
    {% if cookiecutter.enable_api_docs == "yes" %}"drf-spectacular>=0.27",
    {% endif %}
]

[dependency-groups]
dev = [
    "pre-commit>=4.0",
    "ruff>=0.11",
    "pytest>=8",
    "pytest-cov>=4",
    "pytest-django>=4.5",
    "pytest-mock>=3",
    "pytest-env>=1.0",
]

# ── ruff ──────────────────────────────────────
[tool.ruff]
line-length = 120
target-version = "py{{ cookiecutter.python_version | replace('.', '') }}"
exclude = [
    ".git",
    "venv",
    ".venv",
    "__pypackages__",
    ".ruff_cache",
    "migrations",
]

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "UP"]
extend-ignore = ["E402"]
fixable = ["ALL"]
extend-safe-fixes = ["UP"]

[tool.ruff.lint.extend-per-file-ignores]
"config/**" = ["F405", "F403"]  # config 模块使用 import * 模式

[tool.ruff.format]
docstring-code-format = true

# ── pytest ────────────────────────────────────
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "{{ cookiecutter.project_name }}.settings"
python_files = ["test_*.py", "tests.py"]
testpaths = ["tests"]
console_output_style = "count"
log_level = "ERROR"
filterwarnings = [
    "error",
    "ignore::DeprecationWarning",
    "ignore::ResourceWarning",
]
env = [
    "DJANGO_ENV=testing",
]

# ── coverage ──────────────────────────────────
[tool.coverage.run]
omit = [
    "*/test*",
    "*/migrations*",
    "*/__init__.py",
    "manage.py",
    "*/settings.py",
    "*/config/**",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",]
skip_empty = true
show_missing = true
```

**借鉴 drf_resource 和 bk-monitor 的优化**：

| 配置项 | 来源 | 说明 |
|--------|------|------|
| `classifiers` | drf_resource | PyPI 分类标签，标明支持的 Django/Python 版本 |
| `dependency-groups.dev` | drf_resource + bk-monitor | PEP 735 开发依赖组（pre-commit/ruff/pytest 全家桶） |
| `[tool.ruff.lint]` | drf_resource + bk-monitor | E4/E7/E9/F/UP 规则集，extend-safe-fixes 启用 UP 自动修复 |
| `extend-per-file-ignores` | bk-monitor | `config/**` 忽略 F403/F405（import * 模式） |
| `[tool.coverage.run]` | bk-monitor | 排除测试/migrations/配置文件的覆盖率统计 |
| `[tool.coverage.report]` | bk-monitor | `skip_empty` 跳过空文件，`show_missing` 显示未覆盖行号 |
| `filterwarnings` | bk-monitor | warning 转 error，忽略 DeprecationWarning |
| `env` (pytest) | bk-monitor | 测试环境自动注入 `DJANGO_ENV=testing` |

### 模板更新策略

```
创建项目:   cruft create https://github.com/HACK-WU/drf-resource-template
检查更新:   cruft check
查看差异:   cruft diff
合并更新:   cruft update
```

**版本兼容策略**：
- 模板仓库使用语义化版本（semver）
- `cookiecutter.json` 变量向后兼容：新增变量必须有默认值
- cruft update 生成 diff 供用户逐文件 review，不会自动覆盖已有修改

### 与 bk-resource 的差异

| 维度 | bk-resource | drf-resource-template |
|------|------------|----------------------|
| 模板位置 | 同仓库 `template/` | 独立仓库 |
| 版本管理 | 与框架同步 | 独立发版 |
| 功能开关 | 无（3 个变量） | 8 个变量 + 6 个条件渲染维度 |
| 配置架构 | 单文件 | 13 个功能模块 + 2 个角色配置 |
| 角色分离 | 无 | web + worker |
| 蓝鲸耦合 | 强耦合 blueapps | 无耦合 |

### 异常处理

| 场景 | 行为 | 对外暴露 |
|------|------|---------|
| 生成的项目 pip install 失败（drf_resource 不在 PyPI） | `.env.example` 中提供 Git 安装方式 | 是，文档引导 |
| 环境变量覆盖值类型不匹配 | 注入为字符串，用户自行转换 | 否，使用者责任 |
