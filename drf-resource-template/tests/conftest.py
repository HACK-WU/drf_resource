"""Shared fixtures for drf-resource-template tests."""
import shutil
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIR = Path(__file__).parent.parent


@pytest.fixture
def template_dir():
    """Return the absolute path to the cookiecutter template directory."""
    return str(TEMPLATE_DIR)


@pytest.fixture
def default_context():
    """Return the default cookiecutter context (matches cookiecutter.json defaults)."""
    return {
        "project_name": "test_project",
        "project_description": "A test project",
        "author_name": "Test Author",
        "python_version": "3.12",
        "database_backend": "sqlite",
        "enable_celery": "no",
        "enable_redis_cache": "no",
        "enable_cors": "no",
        "enable_i18n": "no",
        "enable_api_docs": "no",
    }


@pytest.fixture
def full_context():
    """Return context with all features enabled."""
    return {
        "project_name": "test_project",
        "project_description": "A full-featured test project",
        "author_name": "Test Author",
        "python_version": "3.12",
        "database_backend": "sqlite",
        "enable_celery": "yes",
        "enable_redis_cache": "yes",
        "enable_cors": "yes",
        "enable_i18n": "yes",
        "enable_api_docs": "yes",
    }


@pytest.fixture
def render_template(tmp_path, template_dir):
    """Render the cookiecutter template into a temporary directory.

    Returns a callable that accepts extra_context overrides.
    """

    def _render(extra_context=None, **kwargs):
        context = {
            "project_name": "test_project",
            "project_description": "A test project",
            "author_name": "Test Author",
            "python_version": "3.12",
            "database_backend": "sqlite",
            "enable_celery": "no",
            "enable_redis_cache": "no",
            "enable_cors": "no",
            "enable_i18n": "no",
            "enable_api_docs": "no",
        }
        if extra_context:
            context.update(extra_context)
        context.update(kwargs)

        output_dir = str(tmp_path)
        result_dir = cookiecutter(
            template_dir,
            output_dir=output_dir,
            no_input=True,
            extra_context=context,
        )
        return Path(result_dir)

    return _render
