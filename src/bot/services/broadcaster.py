import asyncio
import logging

from aiogram import Bot, exceptions
from loguru import logger

from src.kommo.author import Author


async def send_message(
    bot: Bot,
    user: Author,
    text: str,
    keyboard=None,
    disable_notification: bool = False,
) -> bool:
    try:
        await bot.send_message(
            user.telegram_id,
            text,
            reply_markup=keyboard,
            disable_notification=disable_notification,
        )
    except exceptions.TelegramBadRequest:
        logging.exception(f"Target [ID:{user.telegram_id}]: failed")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user.telegram_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user.telegram_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_message(bot, user, text, keyboard)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user.telegram_id}]: failed")
    else:
        logging.info(f"Target [ID:{user.telegram_id}]: success")
        return True
    return False


async def broadcast(
    bot: Bot, users: list[Author], text: str, keyboard=None
) -> list[Author]:
    """
    Simple broadcaster
    :return: Count of messages
    """
    count = []
    try:
        for user in users:
            if await send_message(bot, user, text, keyboard):
                count.append(user)
            await asyncio.sleep(
                0.05
            )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logger.info(f"{len(count)} messages successful sent.")

    return count