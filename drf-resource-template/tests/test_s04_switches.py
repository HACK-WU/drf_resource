"""S-04: 功能开关测试用例"""
import sys
from pathlib import Path

import pytest
import tomllib


# ── TC-S04-01-01: enable_celery 开关 ───────────────────────────────────
class TestCelerySwitch:
    """enable_celery 开关测试"""

    def test_celery_yes_creates_celery_dir(self, render_template):
        """TC-S04-01-01a: enable_celery="yes" 时 config/celery/ 目录存在"""
        project_dir = render_template(enable_celery="yes")
        celery_dir = project_dir / "config" / "celery"
        assert celery_dir.is_dir(), f"目录不存在: {celery_dir}"

    def test_celery_no_removes_celery_dir(self, render_template):
        """TC-S04-01-01b: enable_celery="no" 时 config/celery/ 目录不存在"""
        project_dir = render_template(enable_celery="no")
        celery_dir = project_dir / "config" / "celery"
        assert not celery_dir.exists(), f"目录不应存在: {celery_dir}"


# ── TC-S04-01-02: enable_cors 开关 ────────────────────────────────────
class TestCorsSwitch:
    """enable_cors 开关测试"""

    def test_cors_yes_includes_corsheaders(self, render_template):
        """TC-S04-01-02a: enable_cors="yes" 时 apps.py 包含 corsheaders"""
        project_dir = render_template(enable_cors="yes")
        apps_file = project_dir / "config" / "defaults" / "apps.py"
        content = apps_file.read_text()
        assert "corsheaders" in content, "apps.py 应包含 corsheaders"

    def test_cors_no_excludes_corsheaders(self, render_template):
        """TC-S04-01-02b: enable_cors="no" 时 apps.py 不包含 corsheaders"""
        project_dir = render_template(enable_cors="no")
        apps_file = project_dir / "config" / "defaults" / "apps.py"
        content = apps_file.read_text()
        assert "corsheaders" not in content, "apps.py 不应包含 corsheaders"


# ── TC-S04-01-03: enable_i18n 开关 ────────────────────────────────────
class TestI18nSwitch:
    """enable_i18n 开关测试"""

    def test_i18n_yes_includes_locale_middleware(self, render_template):
        """TC-S04-01-03a: enable_i18n="yes" 时 apps.py 包含 LocaleMiddleware"""
        project_dir = render_template(enable_i18n="yes")
        apps_file = project_dir / "config" / "defaults" / "apps.py"
        content = apps_file.read_text()
        assert "LocaleMiddleware" in content, "apps.py 应包含 LocaleMiddleware"

    def test_i18n_no_excludes_locale_middleware(self, render_template):
        """TC-S04-01-03b: enable_i18n="no" 时 apps.py 不包含 LocaleMiddleware"""
        project_dir = render_template(enable_i18n="no")
        apps_file = project_dir / "config" / "defaults" / "apps.py"
        content = apps_file.read_text()
        assert "LocaleMiddleware" not in content, "apps.py 不应包含 LocaleMiddleware"


# ── TC-S04-01-04: enable_api_docs 开关 ──────────────────────────────────
class TestApiDocsSwitch:
    """enable_api_docs 开关测试"""

    def test_api_docs_yes_includes_drf_spectacular(self, render_template):
        """TC-S04-01-04a: enable_api_docs="yes" 时 apps.py 包含 drf_spectacular"""
        project_dir = render_template(enable_api_docs="yes")
        apps_file = project_dir / "config" / "defaults" / "apps.py"
        content = apps_file.read_text()
        assert "drf_spectacular" in content, "apps.py 应包含 drf_spectacular"

    def test_api_docs_no_excludes_drf_spectacular(self, render_template):
        """TC-S04-01-04b: enable_api_docs="no" 时 apps.py 不包含 drf_spectacular"""
        project_dir = render_template(enable_api_docs="no")
        apps_file = project_dir / "config" / "defaults" / "apps.py"
        content = apps_file.read_text()
        assert "drf_spectacular" not in content, "apps.py 不应包含 drf_spectacular"


# ── TC-S04-01-05: enable_redis_cache 开关 ──────────────────────────────
class TestRedisCacheSwitch:
    """enable_redis_cache 开关测试"""

    def test_redis_cache_yes_includes_get_redis_cache_config(self, render_template):
        """TC-S04-01-05a: enable_redis_cache="yes" 时 cache.py 包含 get_redis_cache_config"""
        project_dir = render_template(enable_redis_cache="yes")
        cache_file = project_dir / "config" / "defaults" / "cache.py"
        content = cache_file.read_text()
        assert "get_redis_cache_config" in content, "cache.py 应包含 get_redis_cache_config"

    def test_redis_cache_no_excludes_get_redis_cache_config(self, render_template):
        """TC-S04-01-05b: enable_redis_cache="no" 时 cache.py 不包含 get_redis_cache_config"""
        project_dir = render_template(enable_redis_cache="no")
        cache_file = project_dir / "config" / "defaults" / "cache.py"
        content = cache_file.read_text()
        assert "get_redis_cache_config" not in content, "cache.py 不应包含 get_redis_cache_config"


# ── TC-S04-01-06: 全开关关闭渲染成功 ──────────────────────────────────
class TestAllSwitchesOff:
    """所有功能开关关闭渲染成功测试"""

    def test_all_switches_off_renders_successfully(self, render_template):
        """TC-S04-01-06: 所有 enable_xxx="no" 渲染成功，目录存在"""
        project_dir = render_template(
            enable_celery="no",
            enable_redis_cache="no",
            enable_cors="no",
            enable_i18n="no",
            enable_api_docs="no",
        )
        assert project_dir.is_dir(), f"项目目录不存在: {project_dir}"
        assert (project_dir / "manage.py").is_file(), "manage.py 不存在"
        assert (project_dir / "config").is_dir(), "config 目录不存在"


# ── TC-S04-02-01: requirements.txt 条件依赖 celery ──────────────────────
class TestRequirementsCelery:
    """requirements.txt celery 条件依赖测试"""

    def test_celery_yes_includes_celery_requirement(self, render_template):
        """TC-S04-02-01a: enable_celery="yes" 时 requirements.txt 包含 celery>="""
        project_dir = render_template(enable_celery="yes")
        requirements_file = project_dir / "requirements.txt"
        content = requirements_file.read_text()
        assert "celery>=" in content, "requirements.txt 应包含 celery>="

    def test_celery_no_excludes_celery_requirement(self, render_template):
        """TC-S04-02-01b: enable_celery="no" 时 requirements.txt 不包含 celery>="""
        project_dir = render_template(enable_celery="no")
        requirements_file = project_dir / "requirements.txt"
        content = requirements_file.read_text()
        assert "celery>=" not in content, "requirements.txt 不应包含 celery>="


# ── TC-S04-02-02: requirements.txt 条件依赖数据库 ──────────────────────
class TestRequirementsDatabase:
    """requirements.txt 数据库条件依赖测试"""

    def test_mysql_includes_pymysql(self, render_template):
        """TC-S04-02-02a: database_backend="mysql" 时 requirements.txt 包含 pymysql"""
        project_dir = render_template(database_backend="mysql")
        requirements_file = project_dir / "requirements.txt"
        content = requirements_file.read_text()
        assert "pymysql" in content, "requirements.txt 应包含 pymysql"

    def test_postgresql_includes_psycopg2(self, render_template):
        """TC-S04-02-02b: database_backend="postgresql" 时 requirements.txt 包含 psycopg2"""
        project_dir = render_template(database_backend="postgresql")
        requirements_file = project_dir / "requirements.txt"
        content = requirements_file.read_text()
        assert "psycopg2" in content, "requirements.txt 应包含 psycopg2"


# ── TC-S04-02-03: pyproject.toml 条件依赖 ──────────────────────────────
class TestPyprojectTomlDependencies:
    """pyproject.toml 条件依赖测试"""

    def test_celery_yes_includes_celery_in_pyproject(self, render_template):
        """TC-S04-02-03: enable_celery="yes" 时 pyproject.toml dependencies 包含 celery"""
        project_dir = render_template(enable_celery="yes")
        pyproject_file = project_dir / "pyproject.toml"
        content = pyproject_file.read_bytes()
        pyproject_data = tomllib.loads(content.decode("utf-8"))
        dependencies = pyproject_data.get("project", {}).get("dependencies", [])
        celery_found = any("celery" in dep for dep in dependencies)
        assert celery_found, "pyproject.toml dependencies 应包含 celery"
