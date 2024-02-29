import asyncio
import json
from typing import List, Optional

from aiogram import types
from loguru import logger

from src.bot.keyboards.author import mailing_buttons
from src.bot.misc import bot, redis_client
from src.bot.services.broadcaster import broadcast, send_message
from src.crm.author import Author
from src.crm.lead import Lead
from src.db.schemas import LeadSchema
from src.db.services.author import get_not_busyness_authors


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


async def send_auction_message(author_id: int, lead: LeadSchema):
    message = (
        f"\t🟢 НОВЕ ЗАМОВЛЕННЯ 🟢"
        f"🆔: {lead.id}"
        f"◾️ Спеціальність: {lead.speciality}"
        f"◽️ Вид роботи: {lead.work_type}"
        f"◾️ Тема: {lead.thema}"
        f"◽️ Обсяг: {lead.pages} ст."
        f"◾️ Унікальність: {lead.uniqueness}"
        f"◽️ Дедлайн: {lead.deadline_for_author}"
        f"◾️ Коментар: {lead.note}"
        f"💸 Ціна: {lead.expenses}"
    )

    is_success = await send_message(
        bot,
        author_id,
        message,
        keyboard=mailing_buttons(lead.id, "public").as_markup(one_time_keyboard=True),
    )
    return is_success


async def send_private_auction_messages(author_ids: List[int], lead: LeadSchema):
    message = (
        "\t🟡АУКЦІОН🟡\n"
        f"🆔: {lead.id}\n"
        f"◾️ Спеціальність: {lead.speciality}\n"
        f"◽️ Вид роботи: {lead.work_type}\n"
        f"◾️ Тема: {lead.thema}\n"
        f"◽️ Обсяг {lead.pages} ст.\n"
        f"◾️ Унікальність: {lead.uniqueness}\n"
        f"◽️ Дедлайн: {lead.deadline_for_author}\n"
        f"◾️ Коментар: {lead.note}\n"
    )

    await broadcast(
        bot,
        author_ids,
        message,
        keyboard=mailing_buttons(lead.id, "private").as_markup(),
    )


async def wait_auction_answer(lead: LeadSchema, author_id) -> Optional[str]:
    time = 0
    while True:
        await asyncio.sleep(5)

        answer = await get_answer(lead.id, author_id)

        if answer in ["прийняти", "відхилити"]:
            return answer

        if time >= 300:
            await send_message(
                bot,
                author_id,
                "Час вийшов!",
                keyboard=types.ReplyKeyboardRemove(),
            )
            break

        time += 5


async def find_authors(lead: LeadSchema, delay: int = 0) -> tuple[bool, LeadSchema]:
    await asyncio.sleep(delay)

    authors = await get_not_busyness_authors()
    authors = list(
        filter(
            lambda s: lead.speciality in s.specialties if s.specialties else [],
            authors,
        )
    )

    logger.info(f"Deal {lead.id} has {len(authors)} authors")

    if len(authors) < 1:
        return (False, lead)

    authors = sorted(authors, key=lambda s: s.bussynes + lead.koef)

    flag = False
    for author in authors:
        if await send_auction_message(author.id, lead):
            flag = True

            answer = await wait_auction_answer(lead, author.id)

            if answer == "прийняти":
                bussynes, open_leads = await update_busyness(lead.koef, author)
                await Author.update_author_busyness(author.id, bussynes, open_leads)
                await Lead.update_lead_status(lead, 53018611)
                await Lead.update_lead_author(lead, author)

                logger.info(f"Author {author.telegram_id} becomes the owner of the project [{lead.id}]")
                break

    return (flag, lead)


async def search_private_author(lead: Lead, delay: int = 0) -> tuple[bool, Lead]:
    await asyncio.sleep(delay)
    authors = await get_authors_for_auction()
    authors = list(
        filter(
            lambda s: lead.speciality in s.specialties.split(",") if s.specialties else [],
            authors,
        )
    )

    logger.debug(f"Id сделки [{lead.id}], количество авторов [{len(authors)}]")

    if len(authors) < 1:
        return (False, lead)

    author_ids = [author.id for author in authors]
    await send_private_auction_messages(author_ids, lead)

    await asyncio.sleep(1800)

    prices = sended_private_proposal[str(lead.id)]
    prices = sorted(prices, key=lambda s: s[0])

    if len(prices) >= 1:
        money = prices[0][0]
        author = await get_author(telegram_id=prices[0][1])

        bussynes, open_leads = await update_busyness(lead.koef, author)
        await update_author_busyness(author, bussynes, open_leads)
        await Lead.update_lead_price(lead, money)
        await Lead.update_lead_author(lead, author)
        await Lead.update_lead_status(lead, 53018611)

        logger.info(f"Автор [{author.telegram_id}] становиться владельцем проекта [{lead.id}]")

        await send_message(
            bot,
            author.id,
            f"😎Твоя ставка до замовлення ID {lead.id} перемогла! Менеджер зв`яжеться з тобою в скорому часу.",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    if len(prices) >= 2:
        money = prices[1][0]
        author = await get_author(telegram_id=prices[1][1])

        await Lead.update_lead_second_author(lead, author.name)
        await Lead.update_lead_second_price(lead, money)

        logger.info(f"Автор [{author.telegram_id}] становиться запасным владельцем проекта")

    await broadcast(
        bot,
        users,
        "Аукціон завершено!",
        keyboard=types.ReplyKeyboardRemove(),
    )

    return (True, lead)
