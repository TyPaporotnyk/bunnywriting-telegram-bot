from loguru import logger

from src.crm.services.author import get_all_authors
from src.crm.services.lead import get_all_leads
from src.db.services.author import load_crm_authors_to_db
from src.db.services.lead import load_crm_leads_to_db


async def dump():
    await dump_authors()
    await dump_leads()


async def dump_authors():
    authors = await get_all_authors()
    logger.info(f"Collected {len(authors)} authors from crm")

    await load_crm_authors_to_db(authors)


async def dump_leads():
    leads = await get_all_leads()
    logger.info(f"Collected {len(leads)} leads from crm")

    await load_crm_leads_to_db(leads)
