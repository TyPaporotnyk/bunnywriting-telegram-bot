import asyncio

from src.crm.author import Author
from src.crm.lead import Lead
from src.db.services.author import load_crm_authors_to_db
from src.db.services.lead import load_crm_leads_to_db


async def dump():
    await dump_authors()
    await dump_leads()


async def dump_authors():
    crm_authors = await dump_author_task()
    crm_authors = list(set(crm_authors))
    await load_crm_authors_to_db(crm_authors)


async def dump_author_task(page: int = 0, max_page: int = 10):
    crm_authors = []
    while True:
        loaded_crm_author = await Author.get_authors(page)
        crm_authors += loaded_crm_author

        if len(loaded_crm_author) < 250 or page >= max_page:
            break

        page += 1

    return crm_authors


async def dump_leads():
    tasks = [dump_lead_task(10 * page, 10 * (page + 1)) for page in range(7)]
    crm_leads = await asyncio.gather(*tasks)

    crm_leads = list(set(sum(crm_leads, [])))

    await load_crm_leads_to_db(crm_leads)


async def dump_lead_task(page: int, max_page: int):
    crm_leads = []
    while True:
        loaded_crm_laeds = await Lead.get_leads(page)
        crm_leads += loaded_crm_laeds

        if len(loaded_crm_laeds) < 250 or page >= max_page:
            break

        page += 1

    return crm_leads
