import asyncio
from datetime import datetime, time, timedelta

from loguru import logger

from src.auction.find import find_auction_authors, find_private_auction_authors
from src.bot.utils import logging


async def main():
    logger.info("Start auction")
    start_time = time(8, 0)
    end_time = time(22, 0)
    while True:
        now = (datetime.now() + timedelta(hours=2)).time()

        if start_time < now < end_time:
            logger.info("Start auction sennding")
            await find_auction_authors()
            await find_private_auction_authors()

        else:
            logger.info(f"Time is not reachble: {now}")
            await asyncio.sleep(3600)
            continue

        await asyncio.sleep(900)


if __name__ == "__main__":
    logging.setup()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
