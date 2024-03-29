from typing import List

from src.db.database import session_maker
from src.db.models import Lead
from src.db.repositories.lead import LeadRepository
from src.db.schemas import LeadSchema


async def get_current_author_tasks(session, author_id) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_current_author_tasks(author_id)


async def get_current_author_payments(session, author_id) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_current_author_payments(author_id)


async def get_deadlined_author_tasks(session, author_id) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_deadlined_author_tasks(author_id)


async def get_leads_by_status(session, status) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_leads_by_status(status)


async def update_lead_priority(session, lead_id, priority):
    lead_repository = LeadRepository(session)
    return await lead_repository.update_lead_priority(lead_id, priority)


async def update_lead_alert_comment(session, lead_id, alert_comment: str):
    lead_repository = LeadRepository(session)
    return await lead_repository.update_lead_alert_comment(lead_id, alert_comment)


async def load_crm_leads_to_db(leads: List[LeadSchema]):
    async with session_maker() as session:
        lead_repository = LeadRepository(session)

        for lead in leads:
            lead = lead.model_dump()

            lead_db = await lead_repository.get(id=lead["id"])

            if lead_db:
                for key, value in lead.items():
                    setattr(lead_db, key, value)
            else:
                await lead_repository.create(lead)

        await session.commit()
