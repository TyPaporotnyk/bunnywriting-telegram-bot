from typing import List

from sqlalchemy import and_, insert, select, update
from sqlalchemy.exc import NoResultFound

from src.db.models import Author
from src.db.repositories.abstract import Repository


class AuthorRepository(Repository):
    model = Author

    async def get_admin_ids(self):
        stmt = select(self.model.id).filter_by(is_admin=True, is_active=True)
        try:
            res = await self.session.execute(stmt)
            return res.scalars().all()
        except NoResultFound:
            return None

    async def update_author_busyness_and_open_leads(self, author_id, busyness, open_leads):
        stmt = (
            update(self.model)
            .where(self.model.telegram_id == author_id)
            .values(busyness=busyness, open_leads=open_leads)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_author_plane_busyness(self, author_id, plane_busyness):
        stmt = update(self.model).where(self.model.telegram_id == author_id).values(plane_busyness=plane_busyness)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_author_specialities(self, author_id, specialities):
        stmt = update(self.model).where(self.model.telegram_id == author_id).values(specialities=specialities)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_not_busyness_by_speciality(self, koef: int, speciality: str) -> List[Author]:
        stmt = (
            select(self.model)
            .where(
                and_(
                    (self.model.busyness + koef) < self.model.plane_busyness,
                    self.model.specialities.isnot(None),
                    self.model.specialities.ilike(f"%{speciality}%"),
                    self.model.rating != 0,
                )
            )
            .order_by(self.model.rating.desc(), self.model.busyness.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def register_author(self, author_id, card_number, specialities, telegram_url):
        stmt = (
            update(self.model)
            .where(self.model.telegram_id == author_id)
            .values(card_number=card_number, specialities=specialities, telegram_url=telegram_url)
        )
        await self.session.execute(stmt)
        await self.session.commit()
