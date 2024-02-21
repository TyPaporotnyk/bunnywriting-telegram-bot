import asyncio

from celery import Celery
from celery.schedules import crontab

from src.config import settings

celery_event_loop = asyncio.new_event_loop()


app = Celery(main="telegram_bot", broker=settings.REDIS_URL)
app.autodiscover_tasks()
# celery_app.conf.beat_schedule = {
#     "add-every-30-seconds": {
#         "task": "src.worker.tasks.test_task",
#         "schedule": crontab(minute="*/5", hour="6-23"),
#     },
# }
app.conf.update(broker_connection_retry_on_startup=True)
app.conf.update(timezone="Europe/Kyiv")
