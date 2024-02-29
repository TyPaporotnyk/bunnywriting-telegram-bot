import asyncio
import json
from typing import Optional

from src.bot.misc import redis_client


async def get_answer(lead_id: int, author_id: int) -> Optional[str]:
    lead_answer = await redis_client.get(str(lead_id))

    if not lead_answer:
        lead_answer = {}
    else:
        lead_answer = json.loads(lead_answer)

    return lead_answer.get(str(author_id))


async def set_answer(lead_id: int, author_id: int, answer: str):
    lead_answer = await redis_client.get(str(lead_id))

    if not lead_answer:
        lead_answer = {}
    else:
        lead_answer = json.loads(lead_answer)

    lead_answer[str(author_id)] = answer

    await redis_client.set(lead_id, json.dumps(lead_answer))


async def main():
    await set_answer(234, 234, "Прийняти")
    print(await get_answer(235, 234))


asyncio.run(main())
