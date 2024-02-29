from sqlalchemy import select

from src.db.models import Speciality
from src.db.repositories.abstract import Repository


class SpecialityRepository(Repository):
    model = Speciality

    async def get_specialities_from_list(self, specialties):
        stmt = select(self.model).where(self.model.name.in_(specialties))
        res = await self.session.execute(stmt)
        return res.scalars().all()
