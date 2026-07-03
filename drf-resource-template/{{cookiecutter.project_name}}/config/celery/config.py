"""Celery 配置类 + beat_schedule"""
from celery.schedules import crontab
from django.conf import settings


class Config:
    """Celery 配置"""
    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND

    # 使用 django_celery_beat 的调度器
    beat_scheduler = "django_celery_beat.schedulers.DatabaseScheduler"

    # 序列化
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]

    # 如果是 Web 角色，Celery 任务同步执行（调试用）
    task_always_eager = settings.DJANGO_ROLE != "worker" if hasattr(settings, "DJANGO_ROLE") else False

    # 时区
    timezone = "Asia/Shanghai"

    # 定时任务调度（从 DEFAULT_CRONTAB 动态构建）
    beat_schedule = {}
    # 用户可在 role/worker.py 的 DEFAULT_CRONTAB 中添加定时任务
    # 也可在此直接配置 beat_schedule
