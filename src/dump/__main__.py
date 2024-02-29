import asyncio

from src.dump.dump import dump


async def main():
    await dump()


if __name__ == "__main__":
    asyncio.run(main())
