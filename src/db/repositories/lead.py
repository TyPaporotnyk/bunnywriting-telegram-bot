from datetime import datetime, timedelta

from sqlalchemy import desc, select, update

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

    async def get_admin_urgent_list(self, team_lead, author_id: int | None = None):
        if author_id:
            status_conditions = ["План"]
            stmt = (
                select(self.model)
                .where(
                    (self.model.team_lead == team_lead)
                    & (self.model.status.in_(status_conditions) & (self.model.author_id == author_id))
                )
                .order_by(desc(self.model.deadline_for_author))
            )
            result_first = (await self.session.execute(stmt)).scalars().all()

            status_conditions = ["В роботі", "Правки в роботі"]
            stmt = (
                select(self.model)
                .where(
                    (self.model.team_lead == team_lead)
                    & (self.model.deadline_for_author <= datetime.now() + timedelta(days=3))
                    & (self.model.status.in_(status_conditions))
                    & (self.model.author_id == author_id)
                )
                .order_by(desc(self.model.deadline_for_author))
            )

            second_result = (await self.session.execute(stmt)).scalars().all()

            return second_result + result_first
        else:
            status_conditions = ["План"]
            stmt = (
                select(self.model)
                .where((self.model.team_lead == team_lead) & (self.model.status.in_(status_conditions)))
                .order_by(desc(self.model.deadline_for_author))
            )
            result_first = (await self.session.execute(stmt)).scalars().all()

            status_conditions = ["В роботі", "Правки в роботі"]
            stmt = (
                select(self.model)
                .where(
                    (self.model.team_lead == team_lead)
                    & (self.model.deadline_for_author <= datetime.now() + timedelta(days=3))
                    & (self.model.status.in_(status_conditions))
                )
                .order_by(desc(self.model.deadline_for_author))
            )

            second_result = (await self.session.execute(stmt)).scalars().all()

            return second_result + result_first

    async def get_author_urgent_list(self, author_id):
        status_conditions = ["План"]
        stmt = (
            select(self.model)
            .where((self.model.author_id == author_id) & (self.model.status.in_(status_conditions)))
            .order_by(desc(self.model.deadline_for_author))
        )
        result_first = (await self.session.execute(stmt)).scalars().all()

        status_conditions = ["В роботі", "Правки в роботі"]
        stmt = (
            select(self.model)
            .where(
                (self.model.author_id == author_id)
                & (self.model.deadline_for_author <= datetime.now() + timedelta(days=3))
                & (self.model.status.in_(status_conditions))
            )
            .order_by(desc(self.model.deadline_for_author))
        )

        second_result = (await self.session.execute(stmt)).scalars().all()

        return second_result + result_first

    async def get_author_payments(self, team_lead, author_id):
        status_conditions = [
            "Готово",
            "Робота відправлена",
            "Правки",
            "Правки в роботі",
            "Не відправлено",
        ]
        stmt = select(self.model).where(
            (self.model.team_lead == team_lead)
            & (self.model.author_id == author_id)
            & (self.model.status.in_(status_conditions))
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_overdue_works(self):
        stmt = (
            select(self.model)
            .where((self.model.real_deadline <= datetime.now()) & (self.model.status == "В роботі"))
            .order_by(self.model.real_deadline)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_admin_salary(self, team_lead):
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(days=1)

        stmt = (
            select(self.model)
            .where(
                (self.model.ready_date >= start_of_month)
                & (self.model.ready_date <= end_of_month)
                & (self.model.team_lead == team_lead)
            )
            .order_by(self.model.real_deadline)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
