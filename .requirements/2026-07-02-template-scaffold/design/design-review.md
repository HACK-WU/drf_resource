# 设计文档评审报告

```
🔍 设计文档评审报告
━━━━━━━━━━━━━━━━

文档：.requirements/2026-07-02-template-scaffold/design/
格式：design-craft 多文档
评审时间：2026-07-02

文档清单：
  - DESIGN.md（父文档，4 章）
  - S01_engine_DESIGN.md（脚手架引擎，9 节）
  - S02_config_DESIGN.md（配置架构 + 角色，20 节）
  - S03_integration_DESIGN.md（drf_resource 集成，2 节）
  - S04_switches_DESIGN.md（功能开关 + 依赖，4 节）
```

---

## 🔴 阻断（必须修复）

| # | 维度 | 位置 | 问题描述 | 修改建议 | 来源 |
|---|------|------|---------|---------|------|
| 1 | 质量 | S02 §4-14 (L203-219) | 11 个 config 模块（database/cache/rest_framework/celery/cors/i18n/api_docs/static_files/session/logging/env_override）仅有一行摘要，且标注"完整代码参见原单文档 DESIGN.md（已删除）"。设计文档删除后这些模块的实现细节完全丢失，design-to-code 阶段无法据此生成代码 | 为每个模块补充完整的代码设计（至少含关键 Settings 变量名、默认值、条件渲染逻辑），或标注"design-to-code 时根据 bk-monitor 对应文件参考实现"并给出参考路径 | 阶段2 |
| 2 | 正确性 | S03 §1 (L36-45) | `urls.py` 中 `SpectacularAPIView`/`SpectacularSwaggerView` 在 `urlpatterns` 中被引用，但 `from drf_spectacular.views import ...` 位于文件末尾（L43-45）。Python 模块加载时先执行 `urlpatterns` 赋值，此时名称未定义 → `NameError` | 将 `from drf_spectacular.views import ...` 移到文件顶部（`from django.urls import ...` 之后），`urlpatterns` 之前 | 阶段3 |
| 3 | 正确性 | S01 §3 (L124-129) | `post_gen_project.py` 的文件清理仅删除 `{{ cookiecutter.project_name }}/celery.py`，但 Celery 已重构为 `config/celery/` 目录（含 `__init__.py`、`celery.py`、`config.py` 三个文件）。清理逻辑与当前目录结构不匹配 | 更新清理逻辑为：`import shutil; shutil.rmtree("{{ cookiecutter.project_name }}/config/celery", ignore_errors=True)` | 阶段3 |
| 4 | 正确性 | S04 (L36) | `requirements.txt` 使用 `{{ cookiecutter.python_version >= "3.13" | ternary("5.0", "4.2") }}`，`ternary` 是 Ansible 专用过滤器，cookiecutter 的 Jinja2 环境不包含此过滤器 → 模板渲染时报 `TemplateError` | 改用条件块：`{% if cookiecutter.python_version == "3.13" %}Django>=5.0{% else %}Django>=4.2{% endif %}` | 阶段3 |

---

## 🟡 警告（强烈建议修复）

| # | 维度 | 位置 | 问题描述 | 修改建议 | 来源 |
|---|------|------|---------|---------|------|
| 5 | 质量 | S02 §17 (L310-317) | `dev.py`/`stag.py`/`prod.py` 仅用 3 行表格描述，无实际代码。prod.py 提及"ALLOWED_HOSTS 从环境变量，Redis Session，Celery 并发数"但无实现 | 至少为 `prod.py` 补充关键覆盖代码（ALLOWED_HOSTS 环境变量解析、Redis Session 切换、Celery 并发数配置） | 阶段2 |
| 6 | 完整性 | S03 全文 | S03 缺少"异常处理"章节，而 S01/S02/S04 均有。示例 App 的 Resource 执行失败、Serializer 校验失败等异常路径未定义 | 补充异常处理表：Serializer 校验失败 → 400 + 错误详情；Resource 内部异常 → 500 + 统一错误码 | 阶段1 |
| 7 | 正确性 | S02 §15 (L246) | `role/web.py` 中 `if "redis" in CACHES:` 直接引用 `CACHES` 变量，但该变量定义在 `config/defaults/cache.py` 中，`role/web.py` 未导入它。settings.py 的 `__import__ + dir()` 模式不会将 `CACHES` 注入到 role 模块的命名空间 → `NameError` | 方案 A：在 web.py 中添加 `from config.defaults.cache import CACHES`；方案 B：使用 `from django.conf import settings` 后引用 `settings.CACHES` | 阶段3 |
| 8 | 正确性 | S02 §18 (L358,369) | settings.py 使用 `if _s == _s.upper()` 过滤大写变量名，但此表达式对 `"123"`、`"_"`、`""` 等字符串也返回 True（因为它们不含小写字母）。标准 Django 模式是 `if _s.isupper()`，要求至少一个大写字母且无小写字母 | 将 `if _s == _s.upper()` 改为 `if _s.isupper()` | 阶段3 |
| 9 | 完整性 | 父文档 §3 + S04 | `pyproject.toml` 中写了 `readme = "README.md"`，但设计中没有生成 `README.md` 的方案。`pip install -e .` 或 `python -m build` 会因找不到 README.md 而报错 | 在 S01 中增加 README.md 的设计（含项目说明、安装步骤、使用方法），或在目录结构中补充 | 阶段2 |
| 10 | 完整性 | 父文档 §3 (L110) | 目录结构中 `apps/` 缺少 `__init__.py`。`apps/example/` 有 `__init__.py` 但父级 `apps/` 没有，导致 `apps` 不是合法 Python 包 | 在目录结构中 `apps/` 下补充 `__init__.py` | 阶段1 |
| 11 | 质量 | S02 全文 | `config/defaults/__init__.py`（功能模块汇总导入）的完整代码未出现在 S02 中。该文件是配置加载链的关键节点（settings.py 第 2 步 `from config.defaults import *` 依赖它） | 补充 `defaults/__init__.py` 的完整代码，包含 8 个必须模块 + 4 个条件模块的 import 语句 | 阶段2 |

---

## 🟢 建议（可选优化）

| # | 维度 | 位置 | 问题描述 | 修改建议 | 来源 |
|---|------|------|---------|---------|------|
| 12 | 正确性 | S02 §3 目录结构 | `config/` 作为顶层包放在项目根目录（与 Django 项目包同级），可能与其他第三方库的 `config` 模块冲突。bk-monitor 的做法是 settings.py 也在根目录，config 与之同级 | 可考虑将 `config/` 移入 Django 项目包内（`{{project_name}}/{{project_name}}/config/`），或保持当前结构但在文档中标注此设计决策的理由 | 阶段3 |
| 13 | 质量 | S01 §5 (L170) | `.env.example` 中 `DJANGO_ENV=development` 未注释说明可选值（development/testing/production） | 补充注释：`# DJANGO_ENV: development | testing | production` | 阶段2 |
| 14 | 质量 | S03 §2 (L90-96) | `ExampleResource.perform_request` 返回硬编码 `"id": 1`，示例中未说明这是演示数据 | 添加注释说明 id 为演示值，实际应从数据库获取 | 阶段2 |
| 15 | 一致性 | S01 §3 (L89) | `post_gen_project.py` 中 `ENABLE_CELERY = "{{ cookiecutter.enable_celery }}" == "yes"` 只处理了 celery 的引导信息，未处理其他功能开关（redis_cache/cors/i18n/api_docs）的引导 | 补充其他功能开关的启动提示（如 Redis 连接信息、CORS 配置说明等） | 阶段4 |

---

## 📊 评审统计

```
━━━ 📊 评审统计 ━━━

| 维度     | 🔴  | 🟡  | 🟢  | 合计 |
|----------|-----|-----|-----|------|
| 完整性   | 0   | 3   | 0   | 3    |
| 质量     | 1   | 3   | 3   | 7    |
| 正确性   | 3   | 2   | 1   | 6    |
| 一致性   | 0   | 0   | 1   | 1    |
| 体验     | 0   | 0   | 0   | 0    |
| 合计     | 4   | 8   | 5   | 17   |
```

评审结论：❌ 不通过

下一步建议：
- 修复所有 🔴 阻断项（4 项）后可重新提交评审
- 🟡 警告项（8 项）建议在 design-to-code 前一并修复，避免编码阶段返工
- 修复后建议使用增量再审模式（提供本文档作为前次评审结果）
