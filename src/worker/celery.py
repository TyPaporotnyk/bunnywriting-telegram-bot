from celery import Celery
from celery.schedules import crontab

from src.config import settings

app = Celery(main="telegram_bot", broker=settings.REDIS_URL)
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "dump-crm-models-task": {
        "task": "src.worker.tasks.dump_crm_data_task",
        "schedule": crontab(minute="*/5"),
    },
    "send-team-leads-alerts-task": {
        "task": "src.worker.tasks.send_team_leads_alerts_task",
        "schedule": crontab(minute="0", hour="10"),
    },
}
app.conf.beat_schedule_filename = "data/celerybeat-schedule"
app.conf.update(broker_connection_retry_on_startup=True)
app.conf.update(timezone="Europe/Kyiv")
