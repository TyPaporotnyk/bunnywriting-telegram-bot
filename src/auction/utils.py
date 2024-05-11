import asyncio
from typing import List, Optional

from loguru import logger

from src.bot.services.redis import delete_action, get_public_auction_answer, set_public_auction_answer
from src.crm.lead import Lead, statuses
from src.db.schemas import LeadSchema


async def check_lead_status(lead: LeadSchema) -> bool:
    new_lead = await Lead.get_lead(lead.id)

    return lead.status == new_lead.status


async def update_lead_status(lead: LeadSchema, curr_status: int, feat_status: int):
    order_check = await Lead.get_lead(lead.id)
    if order_check.status == statuses.get(curr_status):
        await Lead.update_lead_status(lead.id, feat_status)
        logger.info(f"Lead {lead.id} change status to {feat_status}")


async def wait_auction_answer(lead: LeadSchema, author_id) -> Optional[str]:
    time = 0

    await delete_action(lead.id)
    await set_public_auction_answer(lead.id, author_id, "wait")
    while True:
        await asyncio.sleep(5)

        answer = await get_public_auction_answer(lead.id, author_id)

        if answer in ["accept", "refuce"] or time >= 300:
            break

        time += 5

    await delete_action(lead.id)
    return answer


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
