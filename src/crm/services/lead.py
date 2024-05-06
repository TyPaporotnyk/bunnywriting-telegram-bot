from loguru import logger

from src.crm import Lead


async def get_all_leads():
    page = 0
    leads = []

    while True:
        received_leads = await Lead.get_leads(page=page)
        leads.extend(received_leads)

        logger.info(f"Received {len(received_leads)} leads by {page + 1} page")

        if len(received_leads) < 250:
            break

        page += 1

    return leads
