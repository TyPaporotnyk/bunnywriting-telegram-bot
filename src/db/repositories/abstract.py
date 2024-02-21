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
            return res.scalar()
        except NoResultFound:
            return None

    async def get_all(self):
        stmt = select(self.model)
        try:
            res = await self.session.execute(stmt)
            return res.scalars().all()
        except NoResultFound:
            return None

    async def create(self, data):
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
