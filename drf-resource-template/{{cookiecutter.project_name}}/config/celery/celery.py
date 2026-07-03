"""Celery app + autodiscover + signals"""
import os

from celery import Celery, platforms
from celery.signals import beat_init, setup_logging
from django.conf import settings
from django.db import close_old_connections

# 允许 root 启动 celery
platforms.C_FORCE_ROOT = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ cookiecutter.project_name }}.settings")

app = Celery("{{ cookiecutter.project_name }}")

# 从 config.celery.config 加载配置
app.config_from_object("config.celery.config:Config")

# 自动发现所有 INSTALLED_APPS 中的 tasks.py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f"Request: {self.request!r}")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """使用 Django 的 LOGGING 配置 Celery 日志"""
    from logging.config import dictConfig
    dictConfig(settings.LOGGING)


@beat_init.connect
def clean_db_connections(sender, **kwargs):
    """beat 启动时清理旧 DB 连接"""
    close_old_connections()
