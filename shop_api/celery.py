import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')

app = Celery('shop_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'clean-unconfirmed-users': {
        'task': 'users.tasks.clean_unconfirmed_users',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2:00 AM
    },
    'send-user-activity-report': {
        'task': 'users.tasks.send_activity_report',
        'schedule': crontab(hour=10, minute=0, day_of_week=1),  # Every Monday at 10:00 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
