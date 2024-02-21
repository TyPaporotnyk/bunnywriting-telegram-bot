from sqlalchemy import insert, select

from src.db.models import Admin
from src.db.repositories.abstract import Repository


class AdminRepository(Repository):
    model = Admin

    async def get_admin_ids(self) -> Admin:
        stmt = select(self.model.id).filter_by(is_active=True)
        res = await self.session.execute(stmt)
        return res.scalars().all()
