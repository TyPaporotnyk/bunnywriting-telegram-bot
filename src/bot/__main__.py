import asyncio

from loguru import logger

from src.bot import handlers, middlewares
from src.bot.misc import bot, dp
from src.bot.utils import logging


async def main():
    middlewares.setup(dp)
    handlers.setup(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.setup()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot has been closed")
