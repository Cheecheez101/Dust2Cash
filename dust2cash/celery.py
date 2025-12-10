import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dust2cash.settings')

app = Celery('dust2cash')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

