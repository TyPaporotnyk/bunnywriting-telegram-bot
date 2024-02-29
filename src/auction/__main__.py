import asyncio
from datetime import datetime, time

from src.auction.find import find_auction_authors
from src.worker.tasks import find_auction_authors_task


async def main():
    start_time = time(8, 0)
    end_time = time(22, 0)
    while True:
        now = datetime.now().time()

        if start_time < now < end_time:
            find_auction_authors()

        else:
            await asyncio.sleep(3600)
            continue

        await asyncio.sleep(900)


if __name__ == "__main__":
    asyncio.run(main())
