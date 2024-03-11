from sqlalchemy import select, update

from src.db.models import Lead
from src.db.repositories.abstract import Repository


class LeadRepository(Repository):
    model = Lead

    async def get_current_author_tasks(self, author_id):
        status_conditions = ["План", "План готовий", "Правки план", "План відправлено", "План затверджено", "В роботі"]
        stmt = select(self.model).where(
            (self.model.author_id == author_id) & (self.model.status.in_(status_conditions))
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_current_author_payments(self, author_id):
        status_conditions = ["Готово/Правки", "Робота відправлена", "Не відправлено", "Правки відправлено", "Готово"]
        stmt = (
            select(self.model)
            .where(
                (self.model.author_id == author_id)
                & (self.model.status.in_(status_conditions))
                & (self.model.expenses != 0)
            )
            .order_by(self.model.priority.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_leads_by_status(self, status):
        stmt = select(self.model).where(self.model.status == status)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def update_lead_priority(self, lead_id, priority):
        stmt = update(self.model).where(self.model.id == lead_id).values(priority=priority)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_lead_alert_comment(self, lead_id, alert_comment: str):
        stmt = update(self.model).where(self.model.id == lead_id).values(alert_comment=alert_comment)
        await self.session.execute(stmt)
        await self.session.commit()
