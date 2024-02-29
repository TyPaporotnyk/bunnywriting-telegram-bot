from sqlalchemy import insert, select, update
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

    async def update_author_business(self, author_id, plane_bussyness):
        stmt = update(self.model).where(self.model.telegram_id == author_id).values(plane_bussyness=plane_bussyness)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_author_specialities(self, author_id, specialities):
        stmt = update(self.model).where(self.model.telegram_id == author_id).values(specialities=specialities)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_not_business(self):
        stmt = select(Author).where(Author.busyness < Author.plane_busyness).order_by(Author.rating.desc())
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
