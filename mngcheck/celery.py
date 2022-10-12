import os
from celery import Celery
from django.apps import apps
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mngcheck.settings')

app = Celery('mngcheck')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.conf.beat_schedule = {
    'send-report-send_view_count_report': {
        'task': 'kkt_check.tasks.send_view_count_report',
        'schedule': crontab(minute=0, hour='9'),  # every three hours ,3,6,9,12,15,18,21
    },
    'send-report-send_contact_count_report': {
        'task': 'kkt_check.tasks.send_contact_count_report',
        'schedule': crontab(minute=0, hour='9'),  # every three hours ,3,6,9,12,15,18,21
    },
}