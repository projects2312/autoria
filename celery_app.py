from celery import Celery
from celery.schedules import crontab

app = Celery(
    'autoria',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

app.conf.beat_schedule = {
    'dump-and-scrape-every-day-at-noon': {
        'task': 'autoria.tasks.dump_and_scrape',
        'schedule': crontab(hour=12, minute=0),
    },
}

app.conf.timezone = 'Europe/Kyiv'

from autoria.tasks import dump_and_scrape
