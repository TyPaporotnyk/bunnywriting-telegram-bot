from loguru import logger

from src.crm import Author


async def get_all_authors():
    page = 0
    authors = []

    while True:
        received_authors = await Author.get_authors(page=page)
        authors.extend(received_authors)

        logger.info(f"Received {len(received_authors)} authors by {page + 1} page")

        if len(received_authors) < 250:
            break

        page += 1

    return authors
