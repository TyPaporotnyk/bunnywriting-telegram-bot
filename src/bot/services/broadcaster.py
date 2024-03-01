import asyncio
import logging

from aiogram import Bot, exceptions


async def send_message(bot: Bot, author_id: int, message: str, keyboard=None) -> bool:
    # TODO: Тут нужно переписать и сделать красивее
    try:
        await bot.send_message(author_id, message, reply_markup=keyboard)
    except exceptions.TelegramBadRequest:
        logging.exception(f"Target [ID:{author_id}]: failed")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{author_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as e:
        logging.error(f"Target [ID:{author_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return await bot.send_message(author_id, message)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{author_id}]: failed")
    except Exception:
        pass
    else:
        logging.info(f"Target [ID:{author_id}]: success")
        return True
    return False


async def broadcast(bot: Bot, author_ids: list[int], message: str, keyboard=None):
    successful_message_count = 0
    for author_id in author_ids:
        try:
            await send_message(bot, author_id, message, keyboard)
        finally:
            successful_message_count += 1
        await asyncio.sleep(0.05)

    logging.info(f"Successfully sent messages count: {successful_message_count}")
