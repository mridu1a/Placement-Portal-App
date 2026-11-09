from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker='redis://127.0.0.1:6379/0',
        backend='redis://127.0.0.1:6379/0'
    )

    celery.conf.beat_schedule = {
        'daily-reminder': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0),
        },
        'monthly-report': {
            'task': 'tasks.send_monthly_report',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery