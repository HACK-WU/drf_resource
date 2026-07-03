"""测试 S-02 配置架构"""
import pytest


class TestS02Config:
    """S-02 配置架构测试"""

    # ── TC-S02-01: 默认配置加载 ──────────────────────────
    def test_tc_s02_01_01_full_features_render_success(self, render_template):
        """TC-S02-01-01: 全功能开启渲染成功"""
        project_dir = render_template(
            enable_celery="yes",
            enable_cors="yes",
            enable_i18n="yes",
            enable_api_docs="yes"
        )
        assert project_dir.exists()
        assert (project_dir / "config" / "defaults" / "__init__.py").is_file()

    def test_tc_s02_01_02_defaults_init_load_order(self, render_template):
        """TC-S02-01-02: defaults/__init__.py 加载顺序"""
        project_dir = render_template()
        init_file = project_dir / "config" / "defaults" / "__init__.py"
        content = init_file.read_text()

        # 查找 apps 和 env_override 的位置
        apps_pos = content.find("from config.defaults.apps import")
        env_override_pos = content.find("from config.defaults.env_override import")

        # apps 必须在 env_override 之前
        assert apps_pos < env_override_pos, \
            f"apps import (pos={apps_pos}) must come before env_override import (pos={env_override_pos})"

    def test_tc_s02_01_03_conditional_module_skipped(self, render_template):
        """TC-S02-01-03: 条件模块被跳过"""
        project_dir = render_template(enable_celery="no")
        init_file = project_dir / "config" / "defaults" / "__init__.py"
        content = init_file.read_text()

        # celery import 不应该存在
        assert "from config.defaults.celery import" not in content

    # ── TC-S02-02: 角色配置 ──────────────────────────────
    def test_tc_s02_02_01_web_role_config(self, render_template):
        """TC-S02-02-01: Web 角色配置"""
        project_dir = render_template()
        web_py = project_dir / "config" / "role" / "web.py"
        assert web_py.exists(), "config/role/web.py should exist"

    def test_tc_s02_02_02_worker_role_config(self, render_template):
        """TC-S02-02-02: Worker 角色配置"""
        project_dir = render_template(enable_celery="yes")
        worker_py = project_dir / "config" / "role" / "worker.py"
        content = worker_py.read_text()

        assert "MIDDLEWARE = []" in content, \
            "Worker role should have empty MIDDLEWARE"

    def test_tc_s02_02_03_worker_role_celery_integration(self, render_template):
        """TC-S02-02-03: Worker 角色精简"""
        project_dir = render_template(enable_celery="yes")
        worker_py = project_dir / "config" / "role" / "worker.py"
        content = worker_py.read_text()

        assert "django_celery_beat" in content, \
            "Worker role should include django_celery_beat when celery is enabled"

    # ── TC-S02-03: 环境配置 ──────────────────────────────
    def test_tc_s02_03_01_three_env_configs_exist(self, render_template):
        """TC-S02-03-01: 三环境配置文件存在"""
        project_dir = render_template()

        assert (project_dir / "config" / "dev.py").exists(), \
            "config/dev.py should exist"
        assert (project_dir / "config" / "stag.py").exists(), \
            "config/stag.py should exist"
        assert (project_dir / "config" / "prod.py").exists(), \
            "config/prod.py should exist"

    def test_tc_s02_03_02_dev_py_has_debug(self, render_template):
        """TC-S02-03-02: dev.py 含 DEBUG"""
        project_dir = render_template()
        dev_py = project_dir / "config" / "dev.py"
        content = dev_py.read_text()

        assert "DEBUG = True" in content, \
            "config/dev.py should contain DEBUG = True"

    def test_tc_s02_03_03_prod_py_has_debug_false(self, render_template):
        """TC-S02-03-03: prod.py 含 DEBUG=False"""
        project_dir = render_template()
        prod_py = project_dir / "config" / "prod.py"
        content = prod_py.read_text()

        assert "DEBUG = False" in content, \
            "config/prod.py should contain DEBUG = False"

    # ── TC-S02-04: settings.py 加载链 ───────────────────
    def test_tc_s02_04_01_settings_py_load_chain(self, render_template):
        """TC-S02-04-01: settings.py 加载链"""
        project_dir = render_template()
        settings_py = project_dir / "test_project" / "settings.py"
        content = settings_py.read_text()

        assert "from config import" in content, \
            "settings.py should import from config"
        assert "from config.defaults import" in content, \
            "settings.py should import from config.defaults"
        assert "from local_settings import" in content, \
            "settings.py should import from local_settings"

    def test_tc_s02_04_02_settings_py_role_routing(self, render_template):
        """TC-S02-04-02: settings.py 角色路由"""
        project_dir = render_template()
        settings_py = project_dir / "test_project" / "settings.py"
        content = settings_py.read_text()

        assert "DJANGO_ROLE" in content, \
            "settings.py should reference DJANGO_ROLE"
        assert "config.role" in content, \
            "settings.py should route to config.role"

    def test_tc_s02_04_03_settings_py_env_routing(self, render_template):
        """TC-S02-04-03: settings.py 环境路由"""
        project_dir = render_template()
        settings_py = project_dir / "test_project" / "settings.py"
        content = settings_py.read_text()

        assert "DJANGO_ENV" in content, \
            "settings.py should reference DJANGO_ENV"
        assert "ENV_MODULE_MAP" in content, \
            "settings.py should define ENV_MODULE_MAP"

    # ── TC-S02-05: 配置工具 ──────────────────────────────
    def test_tc_s02_05_01_environment_py_exists(self, render_template):
        """TC-S02-05-01: environment.py 存在且正确"""
        project_dir = render_template()
        env_py = project_dir / "config" / "tools" / "environment.py"
        content = env_py.read_text()

        assert "ENVIRONMENT" in content, \
            "config/tools/environment.py should define ENVIRONMENT"
        assert "RUN_MODE" in content, \
            "config/tools/environment.py should define RUN_MODE"

    def test_tc_s02_05_02_mysql_py_exists(self, render_template):
        """TC-S02-05-02: mysql.py 存在且正确"""
        project_dir = render_template(database_backend="mysql")
        mysql_py = project_dir / "config" / "tools" / "mysql.py"
        content = mysql_py.read_text()

        assert "get_mysql_settings" in content, \
            "config/tools/mysql.py should define get_mysql_settings"
