import asyncio
import logging
from typing import List

from src.bot.misc import bot
from src.bot.services.broadcaster import broadcast
from src.worker.celery import app

logger = logging.getLogger(__name__)


@app.task
def test_task():
    logger.info("Test message")


@app.task
def send_user_messages_task(author_ids: List[int], messsage: str):
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(broadcast(bot, author_ids, messsage))
