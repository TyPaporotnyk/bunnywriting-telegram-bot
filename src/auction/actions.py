import asyncio
from typing import List, Optional

from aiogram import types
from loguru import logger

from src.bot.keyboards.author import mailing_buttons
from src.bot.misc import bot
from src.bot.services.broadcaster import broadcast, send_message
from src.bot.services.redis import (
    delete_action,
    get_lead_answers,
    get_public_auction_answer,
    set_public_auction_answer,
)
from src.crm.author import Author
from src.crm.lead import Lead
from src.db.schemas import LeadSchema
from src.db.services.author import get_not_busyness_authors, update_author_busyness_and_open_leads


async def send_auction_message(author_id: int, lead: LeadSchema):
    message = (
        "\t🟢 НОВЕ ЗАМОВЛЕННЯ 🟢\n"
        f"🆔: #{lead.id}\n"
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


async def send_private_auction_messages(author_ids: List[int], lead: LeadSchema):
    message = (
        "\t🟡АУКЦІОН🟡\n"
        f"🆔: #{lead.id}\n"
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
        keyboard=mailing_buttons(lead.id, "private").as_markup(one_time_keyboard=True),
    )


async def wait_auction_answer(lead: LeadSchema, author_id) -> Optional[str]:
    time = 0
    answer = ""

    await delete_action(lead.id)
    await set_public_auction_answer(lead.id, author_id, "wait")
    while True:
        await asyncio.sleep(5)

        answer = await get_public_auction_answer(lead.id, author_id)

        if answer in ["accept", "refuce"] or time >= 300:
            break

        time += 5

    await delete_action(lead.id)
    return answer


async def find_authors(lead: LeadSchema, delay: int = 0) -> tuple[bool, LeadSchema]:
    await asyncio.sleep(delay)

    authors = await get_not_busyness_authors(lead.koef, lead.speciality)
    logger.info(f"Deal {lead.id} has {len(authors)} authors")

    flag = False
    for author in authors:
        if await send_auction_message(author.telegram_id, lead):
            answer = await wait_auction_answer(lead, author.telegram_id)

            if answer == "accept":
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
                    f"Термін прийому завдання #{lead.id} завершився",
                    keyboard=types.ReplyKeyboardRemove(),
                )

    return (flag, lead)


async def find_private_authors(lead: Lead, delay: int = 0) -> tuple[bool, Lead]:
    await asyncio.sleep(delay)

    # Получаем всех авторов которые могут участвовать в приватном аукционе
    authors = await get_not_busyness_authors(lead.speciality)

    logger.info(f"Private deal {lead.id} has {len(authors)} authors")

    if not authors:
        return (False, lead)

    # Получаем id авторов и рассылаем им всем прикглащение на участие
    author_ids = [author.telegram_id for author in authors]
    await delete_action(lead.id)
    for author_id in author_ids:
        await set_public_auction_answer(lead.id, author_id, "wait")
    await send_private_auction_messages(author_ids, lead)

    # Ждет пока авторы успеют дать свои ответы
    # await asyncio.sleep(1800)
    await asyncio.sleep(1800)

    # Получаем результаты аукциона и отправляем сообщения победителям
    author_rates = await get_lead_answers(lead.id)
    await delete_action(lead.id)
    author_ids_with_prices = [
        (author_id, author_rates[author_id]) for author_id in author_rates if author_rates[author_id].isdigit()
    ]
    author_ids_with_prices = sorted(author_ids_with_prices, key=lambda s: int(s[1]))
    logger.debug(author_ids_with_prices)

    if not author_ids_with_prices:
        return (True, lead)

    if len(author_ids_with_prices) >= 1:
        author_data = author_ids_with_prices[0]
        author_id = author_data[0]
        price = author_data[1]

        # Получаем автора по его айди из уже готового списка авторов
        author = [author for author in authors if author.telegram_id == int(author_id)][0]

        open_leads = author.open_leads + 1
        busyness = author.busyness + lead.koef

        # Вносим изменения сразу в базу данных и в CRM
        await update_author_busyness_and_open_leads(author.telegram_id, busyness, open_leads)
        await Author.update_author_busyness_and_open_leads(author.id, busyness, open_leads)
        await Lead.update_lead_author(lead.id, author.custom_id, author.name, author.admin_id)
        await Lead.update_lead_price(lead.id, price)
        await Lead.update_lead_status(lead.id, 53018611)

        logger.info(f"Автор [{author.telegram_id}] становиться владельцем проекта [{lead.id}]")

        await send_message(
            bot,
            author.telegram_id,
            f"😎Твоя ставка до замовлення ID {lead.id} перемогла! Менеджер зв`яжеться з тобою в скорому часу.",
            keyboard=types.ReplyKeyboardRemove(),
        )

    if len(author_ids_with_prices) >= 2:
        author_data = author_ids_with_prices[1]
        author_id = author_data[0]
        price = author_data[1]

        author = [author for author in authors if author.telegram_id == int(author_id)][0]

        await Lead.update_lead_second_author(lead.id, author.name)
        await Lead.update_lead_second_price(lead.id, price)

        logger.info(f"Автор [{author.telegram_id}] становиться запасным владельцем проекта")

    await broadcast(
        bot,
        author_ids,
        f"Термін прийому участі в аукціоні #{lead.id} завершився",
        keyboard=types.ReplyKeyboardRemove(),
    )

    return (True, lead)
