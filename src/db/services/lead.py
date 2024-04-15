from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_urgent_list(session: AsyncSession, team_lead: int) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_admin_urgent_list(team_lead=team_lead)


async def get_author_payment_list(session: AsyncSession, team_lead, author_id) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_author_payments(team_lead=team_lead, author_id=author_id)


async def get_overdue_works(session: AsyncSession) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_overdue_works()


async def get_admin_salary(session: AsyncSession, team_lead: int) -> List[Lead]:
    lead_repository = LeadRepository(session)
    return await lead_repository.get_admin_salary(team_lead)


async def load_crm_leads_to_db(leads: List[LeadSchema]):
    async with session_maker() as session:
        lead_repository = LeadRepository(session)

        for lead in leads:
            lead = lead.model_dump(exclude_unset=True)
            del lead["ready_date"]

            lead_db: Lead = await lead_repository.get(id=lead["id"])

            if lead_db:
                for key, value in lead.items():
                    setattr(lead_db, key, value)

                if lead_db.ready_date is None and lead_db.status in ["Робота відправлена", "Готово"]:
                    lead_db.ready_date = lead_db.updated_at

            else:
                await lead_repository.create(lead)

        await session.commit()
