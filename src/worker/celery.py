import asyncio

from celery import Celery
from celery.schedules import crontab

from src.config import settings

app = Celery(main="telegram_bot", broker=settings.REDIS_URL)
app.autodiscover_tasks()
# app.conf.beat_schedule = {
#     "send-test-message-every-30-seconds": {
#         "task": "src.worker.tasks.test_task",
#         # "schedule": crontab(minute="*/5", hour="6-23"),
#         "schedule": crontab(minute="*/1"),
#     },
# }
# app.conf.beat_schedule_filename = settings.REDIS_URL
app.conf.update(broker_connection_retry_on_startup=True)
app.conf.update(timezone="Europe/Kyiv")
