"""Repository file."""

from abc import ABC, abstractmethod

from sqlalchemy import insert, select
from sqlalchemy.exc import NoResultFound


class ABCRepository(ABC):
    @abstractmethod
    async def get(self, **filter_by):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self, **data):
        raise NotImplementedError


class Repository(ABC):
    model = None

    def __init__(self, session) -> None:
        self.session = session

    async def get(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        try:
            res = await self.session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            return None

    async def get_all(self):
        stmt = select(self.model)
        try:
            res = await self.session.execute(stmt)
            return res
        except NoResultFound:
            return None

    async def create(self, **data):
        stmt = insert(self.model).values(**data)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.inserted_primary_key[0]
