import asyncio
import logging

from aiogram import Bot, exceptions


async def send_message(bot: Bot, author_id: int, message: str, keyboard=None) -> bool:
    try:
        await bot.send_message(author_id, message, reply_markup=keyboard)
        logging.info(f"Message sent successfully to [ID:{author_id}]")
        return True
    except exceptions.TelegramForbiddenError:
        logging.error(f"Failed to send message to [ID:{author_id}]. Forbidden error.")
    except exceptions.TelegramRetryAfter as e:
        logging.error(f"Flood limit exceeded for [ID:{author_id}]. Sleeping for {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return await send_message(bot, author_id, message)  # Рекурсивный вызов после ожидания
    except Exception:
        logging.exception(f"An unexpected error occurred while sending message to [ID:{author_id}].")

    return False


async def broadcast(bot: Bot, author_ids: list[int], message: str, keyboard=None):
    successful_message_count = 0
    for author_id in author_ids:
        try:
            await send_message(bot, author_id, message, keyboard)
            successful_message_count += 1
        except Exception:
            logging.exception(f"Failed to send message to [ID:{author_id}].")
        finally:
            await asyncio.sleep(0.05)

    logging.info(f"Successfully sent messages count: {successful_message_count}")
