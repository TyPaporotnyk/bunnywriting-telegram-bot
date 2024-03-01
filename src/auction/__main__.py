import asyncio
from datetime import datetime, time

from src.auction.find import find_auction_authors, find_private_auction_authors


async def main():
    start_time = time(8, 0)
    end_time = time(22, 0)
    while True:
        now = datetime.now().time()

        if start_time < now < end_time:
            await find_auction_authors()
            await find_private_auction_authors()

        else:
            await asyncio.sleep(3600)
            continue

        await asyncio.sleep(900)


if __name__ == "__main__":
    asyncio.run(main())
