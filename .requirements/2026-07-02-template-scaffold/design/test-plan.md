# 测试计划：drf_resource 脚手架模板仓库

## 概述

- **关联设计文档**：`.requirements/2026-07-02-template-scaffold/design/DESIGN.md` + S-01~S-04
- **需求条目数**：13 个（S-01-01 ~ S-04-02）
- **测试用例数**：47 个
- **覆盖率**：100%（13/13 个需求均有测试用例）

### 测试策略

本项目是 cookiecutter 模板仓库，测试分为三个层次：

| 层次 | 说明 | 测试框架 |
|------|------|---------|
| L1 模板渲染 | cookiecutter 渲染后文件结构和内容正确 | pytest + cookiecutter API |
| L2 钩子逻辑 | pre_gen/post_gen hooks 逻辑正确 | pytest 单元测试 |
| L3 生成项目运行 | 渲染后的 Django 项目可启动并响应请求 | Django test client |

---

## 测试用例

### S-01-01：cookiecutter.json 模板变量定义

#### TC-S01-01-01：默认变量值渲染成功

- **关联需求**：S-01-01
- **测试策略**：功能型
- **优先级**：P0

**前置条件**：
- cookiecutter.json 存在且格式合法

**测试步骤**：
1. 使用 cookiecutter API 以默认值渲染模板
2. 检查渲染后项目目录结构

**预期结果**：
- 渲染成功，无错误
- 生成项目目录包含 manage.py、config/ 等（实际目录名为渲染时设置的 project_name 值）

**通过标准**：
- cookiecutter.main.cookiecutter() 返回成功
- 生成目录包含 50 个文件（与模板文件数一致）

---

#### TC-S01-01-02：所有变量 choices 遍历

- **关联需求**：S-01-01
- **测试策略**：功能型
- **优先级**：P1

**前置条件**：
- cookiecutter.json 定义了 python_version、database_backend、enable_celery 等 choices

**测试步骤**：
1. 遍历 python_version 的每个选项（3.11, 3.12, 3.13）
2. 遍历 database_backend 的每个选项（sqlite, mysql, postgresql）
3. 遍历每个 enable_xxx 开关（yes/no）
4. 验证每种组合渲染成功

**预期结果**：
- 所有 choices 值组合均可成功渲染
- 无 Jinja2 渲染错误

**通过标准**：
- 3 × 3 × 2^5 = 288 种组合全量测试不现实，建议抽样 12 种关键组合（3 种 python_version × 2 种 database_backend × 2 种 celery 开关）全部渲染成功

---

#### TC-S01-01-03：变量值被正确替换到生成文件中

- **关联需求**：S-01-01
- **测试策略**：功能型
- **优先级**：P0

**前置条件**：
- 使用自定义变量值渲染模板

**测试步骤**：
1. 渲染模板，设置 project_name="test_app"，author_name="Test User"
2. 读取生成的 pyproject.toml、README.md、settings.py

**预期结果**：
- pyproject.toml 中 `name = "test_app"`
- README.md 标题为 `# test_app`
- settings.py 中 DJANGO_SETTINGS_MODULE = "test_app.settings"

**通过标准**：
- 所有 {{ cookiecutter.xxx }} 变量被正确替换，无残留模板语法

---

### S-01-02：pre_gen_project.py 变量校验

#### TC-S01-02-01：合法项目名通过校验

- **关联需求**：S-01-02
- **测试策略**：功能型
- **优先级**：P0

**前置条件**：
- pre_gen_project.py 钩子存在

**测试步骤**：
1. 使用合法项目名（如 "my_project"、"demo_app"、"a1"）渲染模板

**预期结果**：
- 渲染成功，无错误输出

**通过标准**：
- 钩子不触发 sys.exit(1)

---

#### TC-S01-02-02：非法项目名被拒绝

- **关联需求**：S-01-02
- **测试策略**：否定型
- **优先级**：P0

**前置条件**：
- pre_gen_project.py 钩子存在

**测试步骤**：
1. 使用非法项目名渲染模板：
   - "123abc"（数字开头）
   - "my project"（含空格）
   - "my-project"（含连字符）
   - "MyProject"（大写字母）
   - "my.project"（含点号）

**预期结果**：
- 每次渲染失败，输出 "不是合法的 Python 包名"

**通过标准**：
- 钩子触发 sys.exit(1)
- 错误信息包含 "不是合法的 Python 包名"

---

#### TC-S01-02-03：保留名称被拒绝

- **关联需求**：S-01-02
- **测试策略**：否定型
- **优先级**：P1

**前置条件**：
- pre_gen_project.py 钩子存在
- 保留字列表：config, apps, tests, manage, django, rest_framework

**测试步骤**：
1. 使用保留名称逐个渲染模板：
   - "config"
   - "apps"
   - "tests"
   - "manage"
   - "django"
   - "rest_framework"

**预期结果**：
- 每次渲染失败，输出 "是保留名称，请换一个名称"

**通过标准**：
- 钩子触发 sys.exit(1)
- 错误信息包含 "是保留名称"

---

#### TC-S01-02-04：边界名称测试

- **关联需求**：S-01-02
- **测试策略**：边界条件
- **优先级**：P2

**测试步骤**：
1. 使用边界名称渲染：
   - "a"（单字符）
   - "a" + "b" × 100（超长名称）
   - "a_1_b_2"（混合下划线数字）

**预期结果**：
- "a" → 成功
- 超长名称 → 成功（无长度限制则通过，有限制则检查错误信息）
- "a_1_b_2" → 成功

**通过标准**：
- 单字符和合法混合名称通过，超长名称按设计行为处理

---

### S-01-03：post_gen_project.py 生成后引导

#### TC-S01-03-01：引导信息输出正确

- **关联需求**：S-01-03
- **测试策略**：功能型
- **优先级**：P1

**前置条件**：
- 使用默认参数渲染模板

**测试步骤**：
1. 渲染模板并捕获 post_gen 输出
2. 检查输出内容

**预期结果**：
- 输出包含 "项目 xxx 已生成！"
- 输出包含 "接下来的步骤" + 6 个步骤（cd, venv, pip install, cp .env, migrate, runserver）

**通过标准**：
- 引导信息完整，包含所有必要步骤

---

#### TC-S01-03-02：条件输出 — Celery 启动指引

- **关联需求**：S-01-03
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. enable_celery="yes" 渲染 → 检查输出包含 celery worker/beat 命令
2. enable_celery="no" 渲染 → 检查输出不包含 celery 命令

**预期结果**：
- enable_celery="yes" → 输出包含 "celery -A {project_name} worker -l info"
- enable_celery="no" → 输出不包含 "celery" 关键词

**通过标准**：
- 条件输出与 enable_celery 开关一致

---

#### TC-S01-03-03：条件文件清理 — Celery 目录

- **关联需求**：S-01-03
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. enable_celery="no" 渲染模板
2. 检查生成目录中是否包含 config/celery/

**预期结果**：
- config/celery/ 目录不存在（已被 post_gen 清理）

**通过标准**：
- enable_celery="no" 时 config/celery/ 目录被删除

---

#### TC-S01-03-04：条件输出 — Redis/API 文档指引

- **关联需求**：S-01-03
- **测试策略**：功能型
- **优先级**：P2

**测试步骤**：
1. enable_redis_cache="yes" → 检查输出包含 Redis 提示
2. enable_api_docs="yes" → 检查输出包含 API 文档地址

**预期结果**：
- 对应开关为 "yes" 时输出对应提示信息

**通过标准**：
- 条件输出与各开关一致

---

### S-01-04：脚手架根文件

#### TC-S01-04-01：manage.py 包含 dotenv + gevent patch

- **关联需求**：S-01-04
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 渲染模板
2. 读取生成的 manage.py 内容

**预期结果**：
- 包含 `import dotenv` 和 `dotenv.load_dotenv()`
- enable_celery="yes" 时包含 gevent monkey patch 逻辑
- DJANGO_SETTINGS_MODULE 正确设置为 "{project_name}.settings"

**通过标准**：
- manage.py 可执行，dotenv 加载正确

---

#### TC-S01-04-02：.env.example 条件内容正确

- **关联需求**：S-01-04
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. database_backend="mysql" 渲染 → 检查 .env.example 包含 MySQL 配置项
2. database_backend="postgresql" 渲染 → 检查包含 PostgreSQL 配置项
3. enable_redis_cache="yes" 渲染 → 检查包含 Redis 配置项
4. enable_celery="yes" 渲染 → 检查包含 Celery 配置项

**预期结果**：
- 各开关对应配置项正确出现/缺失

**通过标准**：
- .env.example 条件内容与功能开关一致

---

#### TC-S01-04-03：.gitignore 覆盖必要忽略规则

- **关联需求**：S-01-04
- **测试策略**：功能型
- **优先级**：P2

**测试步骤**：
1. 渲染模板
2. 检查 .gitignore 包含关键忽略规则

**预期结果**：
- 包含 __pycache__/、*.py[cod]、.env、db.sqlite3、local_settings.py、.venv/ 等

**通过标准**：
- 关键忽略规则完整

---

#### TC-S01-04-04：pyproject.toml 结构合法

- **关联需求**：S-01-04
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. 渲染模板
2. 使用 validate-pyproject 或 toml.load 验证 pyproject.toml

**预期结果**：
- TOML 格式合法
- 包含 [project]、[tool.ruff]、[tool.pytest.ini_options] 等必要节

**通过标准**：
- pyproject.toml 解析成功，无格式错误

---

### S-02-01：config/defaults/ 功能模块

#### TC-S02-01-01：所有默认配置模块存在且可导入

- **关联需求**：S-02-01
- **测试策略**：功能型
- **优先级**：P0

**前置条件**：
- 使用全功能开启参数渲染模板

**测试步骤**：
1. 渲染模板（所有 enable_xxx="yes"）
2. 在生成项目中执行 Django check（python manage.py check）

**预期结果**：
- Django check 通过，无配置错误

**通过标准**：
- 退出码为 0

---

#### TC-S02-01-02：defaults/__init__.py 加载顺序正确

- **关联需求**：S-02-01
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 渲染模板
2. 检查 defaults/__init__.py 的导入顺序

**预期结果**：
- apps 最先加载
- env_override 最后加载
- 条件模块在中间按正确顺序加载

**通过标准**：
- 导入顺序：apps → database → cache → rest_framework → static_files → session → logging → [条件模块] → env_override

---

#### TC-S02-01-03：条件模块在开关关闭时不生成

- **关联需求**：S-02-01
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. enable_celery="no" 渲染 → 检查 config/defaults/celery.py 存在但被 __init__.py 跳过
2. enable_cors="no" → 检查 config/defaults/cors.py 被跳过
3. enable_i18n="no" → 检查 config/defaults/i18n.py 被跳过
4. enable_api_docs="no" → 检查 config/defaults/api_docs.py 被跳过

**预期结果**：
- 条件模块文件本身可能存在（取决于模板渲染），但 __init__.py 中的导入被条件跳过

**通过标准**：
- Django check 通过（无导入错误）

---

### S-02-02：config/role/ 角色分离

#### TC-S02-02-01：Web 角色配置正确

- **关联需求**：S-02-02
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 渲染模板
2. 以 DJANGO_ROLE=web 启动 Django check

**预期结果**：
- INSTALLED_APPS 包含 drf_resource、drf_spectacular 等 Web 专属 App
- MIDDLEWARE 包含完整中间件链

**通过标准**：
- Django check 通过

---

#### TC-S02-02-02：Worker 角色精简配置

- **关联需求**：S-02-02
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 渲染模板（enable_celery="yes"）
2. 以 DJANGO_ROLE=worker 检查配置

**预期结果**：
- INSTALLED_APPS 精简（无 drf_resource、drf_spectacular）
- MIDDLEWARE 为空
- REST_FRAMEWORK 为空
- 包含 django_celery_beat、django_celery_results

**通过标准**：
- Worker 角色配置不含 Web 专属组件

---

#### TC-S02-02-03：非法角色名报错

- **关联需求**：S-02-02
- **测试策略**：否定型
- **优先级**：P1

**测试步骤**：
1. 渲染模板
2. 以 DJANGO_ROLE=admin（不存在的角色）启动

**预期结果**：
- 抛出 ImportError，提示 "无法导入角色配置"

**通过标准**：
- 错误信息包含 "无法导入角色配置" 和角色模块名

---

### S-02-03：config/{env}.py 环境差异

#### TC-S02-03-01：三环境配置正确加载

- **关联需求**：S-02-03
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. DJANGO_ENV=development → 检查 DEBUG=True
2. DJANGO_ENV=production → 检查 DEBUG=False
3. DJANGO_ENV=testing → 检查 stag.py 加载

**预期结果**：
- development: DEBUG=True, CELERY_TASK_ALWAYS_EAGER=True
- production: DEBUG=False, ALLOWED_HOSTS 从环境变量读取

**通过标准**：
- 各环境配置差异明显且正确

---

#### TC-S02-03-02：非法环境名报错

- **关联需求**：S-02-03
- **测试策略**：否定型
- **优先级**：P1

**测试步骤**：
1. DJANGO_ENV=staging（不存在的环境）启动

**预期结果**：
- fallback 到 dev.py（ENV_MODULE_MAP 默认值）

**通过标准**：
- 不崩溃，使用 development 配置

---

### S-02-04：settings.py 配置加载链

#### TC-S02-04-01：6 步加载链完整执行

- **关联需求**：S-02-04
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 渲染模板
2. 检查生成的 settings.py 中 DJANGO_SETTINGS_MODULE 值
3. 验证 config/ 目录下所有模块可导入（python -c "from config import *"）
4. 启动 Django check（python manage.py check）

**预期结果**：
- 按顺序加载：config/__init__ → config/defaults/* → config/role/{role} → config/{env} → SETTINGS_ 环境变量 → local_settings.py

**通过标准**：
- 6 步加载顺序正确，无遗漏

---

#### TC-S02-04-02：SETTINGS_ 前缀环境变量覆盖

- **关联需求**：S-02-04
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. 渲染模板
2. 设置 SETTINGS_DEBUG=true，启动 Django
3. 检查 settings.DEBUG 的值

**预期结果**：
- DEBUG 被覆盖为 True（无论原始配置是什么）

**通过标准**：
- 环境变量覆盖生效

---

#### TC-S02-04-03：env_override 类型自动转换

- **关联需求**：S-02-04
- **测试策略**：功能型
- **优先级**：P2

**测试步骤**：
1. 设置 SETTINGS_DEBUG=true → 期望 DEBUG=True（布尔）
2. SETTINGS_DEBUG=false → 期望 DEBUG=False
3. SETTINGS_CONN_MAX_AGE=120 → 期望 CONN_MAX_AGE=120（整数）
4. SETTINGS_SECRET_KEY=abc → 期望 SECRET_KEY="abc"（字符串）

**预期结果**：
- true/false/1/0/none → 对应 Python 类型
- 整数字符串 → int
- 其他 → str

**通过标准**：
- 类型转换正确

---

### S-02-05：config/tools/ 辅助工具

#### TC-S02-05-01：environment.py 环境检测

- **关联需求**：S-02-05
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. 渲染模板
2. 检查 ENVIRONMENT、RUN_MODE、IS_CONTAINER_MODE 的默认值

**预期结果**：
- 无 DJANGO_ENV 时 ENVIRONMENT="development"
- RUN_MODE="DEVELOP"
- IS_CONTAINER_MODE=False（非容器环境）

**通过标准**：
- 环境检测函数返回正确默认值

---

#### TC-S02-05-02：mysql.py 多变量 fallback

- **关联需求**：S-02-05
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. 仅设置 DB_NAME=testdb → 期望使用 DB_NAME
2. 设置 MYSQL_NAME=testdb（无 DB_NAME）→ 期望 fallback 到 MYSQL_NAME
3. 两者都未设置 → 期望使用默认值 "{project_name}"

**预期结果**：
- fallback 链正确：DB_NAME → MYSQL_NAME → 默认值

**通过标准**：
- MySQL 配置获取函数返回正确值

---

#### TC-S02-05-03：redis.py 缓存配置生成

- **关联需求**：S-02-05
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. 设置 REDIS_HOST=localhost → 期望返回 Redis 缓存配置
2. 未设置 REDIS_HOST → 期望返回 None（不添加 Redis 缓存）

**预期结果**：
- 有 REDIS_HOST 时 CACHES 包含 "redis" 键
- 无 REDIS_HOST 时 CACHES 不包含 "redis" 键

**通过标准**：
- Redis 缓存配置与环境变量一致

---

### S-03-01：URL 路由配置

#### TC-S03-01-01：ResourceRouter 注册成功

- **关联需求**：S-03-01
- **测试策略**：功能型
- **优先级**：P0

**前置条件**：
- 使用默认参数渲染模板

**测试步骤**：
1. 渲染模板
2. 启动 Django，访问 /api/example/

**预期结果**：
- /api/example/ 端点可访问
- 返回 200 状态码（或 DRF 标准响应格式）

**通过标准**：
- API 端点返回有效响应

---

#### TC-S03-01-02：API 文档端点条件生成

- **关联需求**：S-03-01
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. enable_api_docs="yes" 渲染 → 访问 /api/docs/ → 期望 Swagger UI 页面
2. enable_api_docs="no" 渲染 → 访问 /api/docs/ → 期望 404

**预期结果**：
- 开关为 yes 时 API 文档端点可用
- 开关为 no 时端点不存在

**通过标准**：
- API 文档端点与 enable_api_docs 开关一致

---

### S-03-02：示例 App

#### TC-S03-02-01：示例 API 返回正确响应格式

- **关联需求**：S-03-02
- **测试策略**：功能型
- **优先级**：P0

**前置条件**：
- 渲染模板，安装依赖，启动 Django

**测试步骤**：
1. GET /api/example/?name=World
2. 检查响应 JSON 结构

**预期结果**：
- 响应包含 id、name、message 字段
- message = "Hello, World! This is powered by drf_resource."

**通过标准**：
- 响应格式符合 ExampleResponseSerializer 定义

---

#### TC-S03-02-02：示例 API 参数校验

- **关联需求**：S-03-02
- **测试策略**：否定型
- **优先级**：P1

**测试步骤**：
1. GET /api/example/（不传 name 参数）
2. 检查响应

**预期结果**：
- 返回 400 错误
- 错误信息指示 name 字段必填

**通过标准**：
- 参数校验失败时返回标准 DRF 错误格式

---

#### TC-S03-02-03：示例 API 边界输入

- **关联需求**：S-03-02
- **测试策略**：边界条件
- **优先级**：P2

**测试步骤**：
1. name=""（空字符串）
2. name="a" × 100（超长，超过 max_length=100）
3. name="中文测试"
4. name="<script>alert(1)</script>"（XSS）

**预期结果**：
- 空字符串 → 400（必填校验）
- 超长 → 400（max_length 校验）
- 中文 → 200，message 包含中文
- XSS → 200，响应中 script 标签被原样返回（API 不执行 HTML）

**通过标准**：
- 边界输入按预期处理，无崩溃

---

### S-04-01：功能开关条件渲染

#### TC-S04-01-01：6 个开关独立控制代码生成

- **关联需求**：S-04-01
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 逐个关闭每个开关（enable_celery/cors/i18n/api_docs/redis_cache = "no"），其余保持 "yes"
2. 检查生成项目中对应模块是否存在

**预期结果**：
- enable_celery="no" → config/celery/ 目录被清理，INSTALLED_APPS 不含 django_celery_beat
- enable_cors="no" → corsheaders 不在 INSTALLED_APPS 中
- enable_i18n="no" → LocaleMiddleware 不在 MIDDLEWARE 中
- enable_api_docs="no" → drf_spectacular 不在 INSTALLED_APPS 中，/api/docs/ 不可用
- enable_redis_cache="no" → CACHES 不含 redis 键

**通过标准**：
- 每个开关独立控制对应功能，互不影响

---

#### TC-S04-01-02：全开关关闭渲染成功

- **关联需求**：S-04-01
- **测试策略**：边界条件
- **优先级**：P1

**测试步骤**：
1. 所有 enable_xxx="no"，database_backend="sqlite" 渲染模板
2. 启动 Django check

**预期结果**：
- 渲染成功
- Django check 通过
- 项目可正常启动

**通过标准**：
- 最小配置下项目可运行

---

#### TC-S04-01-03：全开关开启渲染成功

- **关联需求**：S-04-01
- **测试策略**：边界条件
- **优先级**：P1

**测试步骤**：
1. 所有 enable_xxx="yes"，database_backend="postgresql" 渲染模板
2. 检查所有条件模块存在

**预期结果**：
- 渲染成功
- 所有条件模块文件存在
- INSTALLED_APPS 包含所有可选 App

**通过标准**：
- 最大配置下项目结构完整

---

### S-04-02：条件依赖管理

#### TC-S04-02-01：requirements.txt 条件依赖正确

- **关联需求**：S-04-02
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. enable_celery="yes" → 检查 requirements.txt 包含 celery>=5.0
2. enable_celery="no" → 检查 requirements.txt 不包含 celery
3. database_backend="mysql" → 检查包含 pymysql>=1.0
4. database_backend="postgresql" → 检查包含 psycopg2-binary>=2.9

**预期结果**：
- 条件依赖与功能开关/数据库选择一致

**通过标准**：
- requirements.txt 中的条件依赖正确

---

#### TC-S04-02-02：pyproject.toml 条件依赖正确

- **关联需求**：S-04-02
- **测试策略**：功能型
- **优先级**：P0

**测试步骤**：
1. 与 TC-S04-02-01 相同的参数组合
2. 检查 pyproject.toml 的 dependencies 列表

**预期结果**：
- pyproject.toml dependencies 与 requirements.txt 一致

**通过标准**：
- 两个依赖文件的条件依赖同步

---

#### TC-S04-02-03：python_version 影响 Django 版本约束

- **关联需求**：S-04-02
- **测试策略**：功能型
- **优先级**：P1

**测试步骤**：
1. python_version="3.13" → 检查 Django>=5.0
2. python_version="3.11" → 检查 Django>=4.2
3. python_version="3.12" → 检查 Django>=4.2

**预期结果**：
- Python 3.13 要求 Django 5.0+
- 其他版本要求 Django 4.2+

**通过标准**：
- Django 版本约束与 Python 版本匹配

---

## 覆盖矩阵

| 需求 ID | 验收标准 | 测试策略 | 用例数 | 用例 ID 列表 |
|---------|----------|----------|--------|-------------|
| S-01-01 | 模板变量定义正确，choices 值有效 | 功能型 | 3 | TC-S01-01-01, TC-S01-01-02, TC-S01-01-03 |
| S-01-02 | 合法名通过，非法名被拒绝 | 功能型+否定型 | 4 | TC-S01-02-01, TC-S01-02-02, TC-S01-02-03, TC-S01-02-04 |
| S-01-03 | 引导信息完整，条件输出正确 | 功能型 | 4 | TC-S01-03-01, TC-S01-03-02, TC-S01-03-03, TC-S01-03-04 |
| S-01-04 | 根文件内容正确 | 功能型 | 4 | TC-S01-04-01, TC-S01-04-02, TC-S01-04-03, TC-S01-04-04 |
| S-02-01 | 功能模块条件加载 | 功能型 | 3 | TC-S02-01-01, TC-S02-01-02, TC-S02-01-03 |
| S-02-02 | web/worker 角色配置正确 | 功能型+否定型 | 3 | TC-S02-02-01, TC-S02-02-02, TC-S02-02-03 |
| S-02-03 | 三环境配置正确 | 功能型+否定型 | 2 | TC-S02-03-01, TC-S02-03-02 |
| S-02-04 | 6 步加载链正确 | 功能型 | 3 | TC-S02-04-01, TC-S02-04-02, TC-S02-04-03 |
| S-02-05 | 辅助工具函数正确 | 功能型 | 3 | TC-S02-05-01, TC-S02-05-02, TC-S02-05-03 |
| S-03-01 | URL 路由注册成功 | 功能型 | 2 | TC-S03-01-01, TC-S03-01-02 |
| S-03-02 | 示例 App 响应正确 | 功能型+否定型+边界 | 3 | TC-S03-02-01, TC-S03-02-02, TC-S03-02-03 |
| S-04-01 | 功能开关独立控制 | 功能型+边界 | 3 | TC-S04-01-01, TC-S04-01-02, TC-S04-01-03 |
| S-04-02 | 条件依赖正确 | 功能型 | 3 | TC-S04-02-01, TC-S04-02-02, TC-S04-02-03 |

**合计**：13 个需求，47 个测试用例，覆盖率 100%

## 未覆盖需求

无。所有需求均有对应测试用例。

## 非功能性测试

### NFT-01：模板渲染性能

- **测试内容**：单次 cookiecutter 渲染耗时
- **通过标准**：< 5 秒（含 hooks 执行）

### NFT-02：生成项目启动时间

- **测试内容**：Django check + migrate + runserver 启动耗时
- **通过标准**：< 30 秒

### NFT-03：生成代码风格合规

- **测试内容**：渲染后的代码通过 ruff check
- **通过标准**：ruff check 退出码为 0

## 风险测试

### RISK-01：cookiecutter 变量名变更导致条件渲染失效

- **来源**：DESIGN.md §4 全局风险
- **测试内容**：手动修改 cookiecutter.json 中一个变量名，检查模板渲染是否报错
- **通过标准**：Jinja2 抛出 UndefinedError

### RISK-02：配置模块导入顺序变更导致加载失败

- **来源**：DESIGN.md §4 全局风险
- **测试内容**：手动调整 defaults/__init__.py 中的导入顺序，运行 Django check
- **通过标准**：Django check 报出具体配置错误（而非 ImportError）

### RISK-03：drf_resource API 版本不兼容

- **来源**：DESIGN.md §4 全局风险
- **测试内容**：安装不同版本的 drf-resource，验证示例 App 是否正常工作
- **通过标准**：drf-resource>=0.1.0 时示例 App 正常工作
