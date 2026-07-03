"""
配置概览索引
================
本文件说明项目中所有配置模块的用途，供开发者快速定位。

配置加载顺序（settings.py）：
    1. config/__init__.py         → 基础常量
    2. config/defaults/           → 功能模块（apps, database, cache, …）
    3. config/role/{role}.py      → 角色差异（web / worker）
    4. config/{env}.py            → 环境差异（dev / stag / prod）
    5. 环境变量覆盖               → SETTINGS_ 前缀注入
    6. local_settings.py          → 开发环境个人覆盖

默认配置模块（config/defaults/）：
    apps.py            - Django 核心（INSTALLED_APPS, MIDDLEWARE, TEMPLATES）
    database.py        - 数据库配置（DATABASES, CONN_MAX_AGE）
    cache.py           - 缓存配置（CACHES）
    rest_framework.py  - REST Framework + drf_resource 配置
    static_files.py    - 静态资源配置（STATIC_URL, STATIC_ROOT）
    session.py         - Session 配置
    logging.py         - 日志配置（LOGGING）
    env_override.py    - 环境变量自动覆盖机制

条件生成的配置模块：
    celery.py          - Celery 异步任务（enable_celery）
    cors.py            - CORS 跨域（enable_cors）
    i18n.py            - 国际化（enable_i18n）
    api_docs.py        - API 文档（enable_api_docs）

角色配置（config/role/）：
    web.py             - Web 角色（添加 CORS/Celery/docs 到 INSTALLED_APPS）
    worker.py          - Worker 角色（精简 INSTALLED_APPS，仅 Celery + 核心）

环境差异配置：
    dev.py / stag.py / prod.py

辅助工具（config/tools/）：
    environment.py     - 环境检测（ENVIRONMENT, RUN_MODE, IS_CONTAINER_MODE）
    redis.py           - Redis 配置辅助函数
"""
