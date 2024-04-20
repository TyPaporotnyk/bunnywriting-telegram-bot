import asyncio
from typing import List, Optional

from aiogram import types
from loguru import logger

from src.auction.utils import wait_auction_answer
from src.bot.keyboards.author import mailing_buttons
from src.bot.misc import bot
from src.bot.services.broadcaster import send_message
from src.crm.author import Author
from src.crm.lead import Lead
from src.db.schemas import LeadSchema
from src.db.services.author import get_not_busyness_authors, update_author_busyness_and_open_leads


async def send_auction_message(author_id: int, lead: LeadSchema):
    message = (
        "\t🟢 НОВЕ ЗАМОВЛЕННЯ 🟢\n"
        f"🆔: {lead.id}\n"
        f"◾️ Спеціальність: {lead.speciality}\n"
        f"◽️ Вид роботи: {lead.work_type}\n"
        f"◾️ Тема: {lead.thema}\n"
        f"◽️ Обсяг: {lead.pages} ст.\n"
        f"◾️ Унікальність: {lead.uniqueness}\n"
        f"◽️ Дедлайн: {lead.deadline_for_author}\n"
        f"◾️ Коментар: {lead.note}\n"
        f"💸 Ціна: {lead.expenses}\n"
    )

    is_success = await send_message(
        bot,
        author_id,
        message,
        keyboard=mailing_buttons(lead.id, "public").as_markup(one_time_keyboard=True),
    )
    return is_success


async def find_authors(lead: LeadSchema, delay: int = 0) -> tuple[bool, LeadSchema]:
    await asyncio.sleep(delay)

    authors = await get_not_busyness_authors(lead.koef, lead.speciality)
    logger.info(f"Deal {lead.id} has {len(authors)} authors")

    flag = False
    for author in authors:
        if await send_auction_message(author.telegram_id, lead):
            answer = await wait_auction_answer(lead, author.telegram_id)

            if answer == "closed":
                logger.info(f"Менеджер віддав завдання {lead.id} іншому автору")
                flag = True
                await send_message(
                    bot,
                    author.telegram_id,
                    f"Менеджер віддав завдання {lead.id} іншому автору",
                    keyboard=types.ReplyKeyboardRemove(),
                )
                break
            elif answer == "accept":
                open_leads = author.open_leads + 1
                busyness = author.busyness + lead.koef

                await update_author_busyness_and_open_leads(author.telegram_id, busyness, open_leads)
                await Author.update_author_busyness_and_open_leads(author.id, busyness, open_leads)
                await Lead.update_lead_author(lead.id, author.custom_id, author.name, author.admin_id)
                await Lead.update_lead_status(lead.id, 53018611)
                flag = True

                logger.info(f"Автор {author.telegram_id} становиться владельцем проекта: {lead.id}")
                break
            elif answer == "refuce":
                logger.info(f"Автор {author.telegram_id} отказался от проекта: {lead.id}")
            else:
                logger.info(f"Автор {author.telegram_id} не отрегировал на проект: {lead.id}")
                await send_message(
                    bot,
                    author.telegram_id,
                    f"Термін прийому завдання {lead.id} завершився",
                    keyboard=types.ReplyKeyboardRemove(),
                )

    return flag, lead
