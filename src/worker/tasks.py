import asyncio
import logging
from typing import List

from src.auction.find import find_auction_authors, find_private_auction_authors
from src.bot.misc import bot
from src.bot.services.broadcaster import broadcast
from src.dump.dump import dump
from src.worker.celery import app

logger = logging.getLogger(__name__)


@app.task
def send_user_messages_task(author_ids: List[int], messsage: str):
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(broadcast(bot, author_ids, messsage))


@app.task
def dump_crm_data_task():
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(dump())


@app.task
def find_auction_authors_task():
    celery_event_loop = asyncio.get_event_loop()
    celery_event_loop.run_until_complete(find_auction_authors())


# @app.task
# def search_authors_for_private_auction():
#     celery_event_loop = asyncio.get_event_loop()
#     celery_event_loop.run_until_complete(search_authors_for_open_lead())
