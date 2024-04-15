import asyncio
from typing import List

from src.alert.admin import send_team_leads_alerts
from src.bot.misc import bot
from src.bot.services.broadcaster import broadcast
from src.dump import dump
from src.worker.celery import app


@app.task
def send_user_messages_task(author_ids: List[int], message: str):
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(broadcast(bot, author_ids, message))


@app.task
def dump_crm_data_task():
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(dump())


@app.task
def send_team_leads_alerts_task():
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(send_team_leads_alerts())
