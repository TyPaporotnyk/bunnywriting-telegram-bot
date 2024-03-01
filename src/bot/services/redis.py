import json
from typing import Optional

from loguru import logger

from src.bot.misc import redis_client


async def delete_action(lead_id: int):
    await redis_client.delete(str(lead_id))


async def get_lead_answers(lead_id: int) -> dict:
    lead_answers = await redis_client.get(str(lead_id))

    if not lead_answers:
        lead_answers = {}
    else:
        lead_answers = json.loads(lead_answers)

    return lead_answers


async def get_public_auction_answer(lead_id: int, author_id: int) -> Optional[str]:
    lead_answers = await get_lead_answers(lead_id)
    return lead_answers.get(str(author_id))


async def set_public_auction_answer(lead_id: int, author_id: int, answer: str):
    lead_answers = await get_lead_answers(lead_id)
    lead_answers[str(author_id)] = answer
    await redis_client.set(lead_id, json.dumps(lead_answers))
