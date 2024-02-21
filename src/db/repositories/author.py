from sqlalchemy import insert, select
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
