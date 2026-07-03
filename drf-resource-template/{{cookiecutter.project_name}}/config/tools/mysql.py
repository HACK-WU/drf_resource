"""MySQL 配置辅助 - 多环境变量 fallback"""
import os


def get_mysql_settings() -> tuple:
    """
    从环境变量获取 MySQL 连接配置
    支持多个环境变量名 fallback，适配不同部署环境
    """
    name = os.getenv("DB_NAME") or os.getenv("MYSQL_NAME", "{{ cookiecutter.project_name }}")
    user = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
    password = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD", "")
    host = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306"))
    return name, host, port, user, password
