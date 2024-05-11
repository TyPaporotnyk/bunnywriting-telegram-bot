import asyncio

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
    logger.info(f"Публичная раздача проекта {lead.id} запустилась")

    authors = await get_not_busyness_authors(lead.koef, lead.speciality)
    logger.info(f"На публичную раздачу проекта {lead.id} нашлось {len(authors)} авторов")

    is_auction_changed = False
    for author in authors:
        is_sent_success = await send_auction_message(author.telegram_id, lead)
        if not is_sent_success:
            logger.info(f"Не удалось отправить сообщение автору {author.custom_id} на участие в проекте {lead.id}")
            continue

        answer = await wait_auction_answer(lead, author.telegram_id)

        if answer == "accept":
            if author.open_leads is None:
                author.open_leads = 0

            open_leads = author.open_leads + 1
            busyness = author.busyness + lead.koef

            await update_author_busyness_and_open_leads(author.telegram_id, busyness, open_leads)
            await Author.update_author_busyness_and_open_leads(author.id, busyness, open_leads)
            await Lead.update_lead_author(lead.id, author.custom_id, author.name, author.admin_id)
            await Lead.update_lead_status(lead.id, 53018611)
            is_auction_changed = True

            logger.info(f"Автор {author.telegram_id} становиться владельцем проекта: {lead.id}")
            break

        elif answer == "refuce":
            logger.info(f"Автор {author.telegram_id} отказался от проекта: {lead.id}")

        else:
            logger.info(f"Автор {author.telegram_id} не отреагировал на проект: {lead.id}")
            await send_message(
                bot,
                author.telegram_id,
                f"Термін прийому завдання {lead.id} завершився",
                keyboard=types.ReplyKeyboardRemove(),
            )

    logger.info(f"Публичная раздача проекта {lead.id} закончился")

    return is_auction_changed, lead
