import asyncio

from loguru import logger

from src.auction.services import private_auction, public_autction
from src.auction.utils import group_leads_by_work_type
from src.crm.lead import Lead, statuses
from src.db.schemas import LeadSchema


async def update_lead_status(lead: LeadSchema, curr_status: int, feat_status: int):
    order_check = await Lead.get_lead(lead.id)
    if order_check.status == statuses.get(curr_status):
        await Lead.update_lead_status(lead.id, feat_status)
        logger.info(f"Lead {lead.id} change status to {feat_status}")


async def find_auction_authors():
    logger.info("Start finding auction authors")
    leads = await Lead.get_leads_by_status(53018603)
    leads = list(filter(lambda x: x.speciality is not None, leads))
    if leads:
        grouped_leads = group_leads_by_work_type(leads)
        logger.info(f"Found {len(leads)} leads grouped by {len(grouped_leads)} work types")

        tasks = [
            public_autction.find_authors(grouped_leads[work][0], delay) for delay, work in enumerate(grouped_leads)
        ]
        task_results = await asyncio.gather(*tasks)

        for task_result in task_results:
            is_finished_task = task_result[0]
            task_lead = task_result[1]
            if not is_finished_task:
                await update_lead_status(task_lead, 53018603, 53018607)
    else:
        logger.info("No new orders")


async def find_private_auction_authors():
    logger.info("Start finding auction authors")
    leads = await Lead.get_leads_by_status(53018607)
    leads = list(filter(lambda x: x.speciality is not None, leads))

    if leads:
        grouped_leads = group_leads_by_work_type(leads)

        tasks = [
            private_auction.find_authors(grouped_leads[work][0], delay) for delay, work in enumerate(grouped_leads)
        ]
        task_results = await asyncio.gather(*tasks)

        for task_result in task_results:
            is_finished_task = task_result[0]
            task_lead = task_result[1]
            if not is_finished_task:
                await update_lead_status(task_lead, 53018607, 53018611)
    else:
        logger.info("No new private orders")
