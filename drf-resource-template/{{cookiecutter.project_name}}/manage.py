"""Django management entry point"""
import os
import sys

import dotenv

dotenv.load_dotenv()

{% if cookiecutter.enable_celery == "yes" %}
# gevent monkey patch for celery + gevent mode
if "celery" in sys.argv and "gevent" in sys.argv:
    from gevent import monkey
    monkey.patch_all()
{% endif %}

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ cookiecutter.project_name }}.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
