import asyncio
from typing import List

from loguru import logger

from src.auction.actions import find_authors
from src.crm.lead import Lead, statuses
from src.db.schemas import LeadSchema


def group_leads_by_work_type(leads: List[LeadSchema]) -> dict[str, List[LeadSchema]]:
    work_type_leads = {}
    for lead in leads:
        lead_work_type = lead.speciality
        if work_type_leads.get(lead_work_type):
            work_type_leads[lead_work_type].append(lead)
        else:
            work_type_leads.setdefault(lead_work_type, [])
            work_type_leads[lead_work_type].append(lead)

    return work_type_leads


async def update_lead_status(lead: Lead, curr_status: int, feat_status: int):
    order_check = await Lead.get_lead(lead.id)
    if order_check.status == statuses.get(curr_status):
        await Lead.update_lead_status(lead.id, feat_status)
        logger.info(f"Lead {lead.id} change status to {feat_status}")


async def find_auction_authors():
    logger.info("Start finding auction authors")
    leads = await Lead.get_leads_by_status(53018603)
    if leads:
        grouped_leads = group_leads_by_work_type(leads)
        logger.info(f"Found {len(leads)} leads grouped by {len(grouped_leads)} work types")

        tasks = [find_authors(grouped_leads[work][0], delay) for delay, work in enumerate(grouped_leads)]
        task_results = await asyncio.gather(*tasks)

        for task_result in task_results:
            is_finifshed_task = task_result[0]
            task_lead = task_result[1]
            if is_finifshed_task:
                await update_lead_status(task_lead, 53018603, 53018607)
    else:
        logger.info("No new orders")


async def find_private_auction_authors():
    pass
    # logger.info("Поиск авторов на задание")

    # leads = await Lead.get_leads_by_status(53018603)
    # if len(leads) > 0:
    #     work_typed_leads = _get_leads_by_work_type(leads)

    #     tasks = [
    #         _search_author(work_typed_leads[work][0], delay)
    #         for delay, work in enumerate(work_typed_leads)
    #     ]

    #     messages = await asyncio.gather(*tasks)
    # for message in messages:
    #     if message[0]:
    #         lead = message[1]
    #         await _check_lead_status(
    #             lead=lead, curr_status=53018603, feat_status=53018607
    #         )
    #     else:
    #         logger.info("Нет свободных авторов")
    # else:
    #     logger.info("Нет новых заказов")
