from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import session_maker
from src.db.models import Author
from src.db.repositories.author import AuthorRepository
from src.db.repositories.specialities import SpecialityRepository
from src.db.schemas import AuthorSchema


async def create_base_author(session: AsyncSession, author_data: dict):
    author_repository = AuthorRepository(session)

    await author_repository.create(author_data)


async def get_author_by_telegram_id(session: AsyncSession, author_id: int) -> Optional[Author]:
    author_repository = AuthorRepository(session)

    author = await author_repository.get(telegram_id=author_id)
    return author


async def get_author_leads(session, author_id):
    author_repository = AuthorRepository(session)
    author = await author_repository.get(id=author_id)

    return author.leads


async def get_not_busyness_authors():
    async with session_maker() as session:
        author_repository = AuthorRepository(session)
        author = await author_repository.get_not_business()

        return author


async def update_author_specialities(session, author_id, specialities):
    author_repository = AuthorRepository(session)
    specialities = "/".join(specialities)

    await author_repository.update_author_specialities(author_id, specialities)


async def update_author_busyness(session, author_id, plane_bussyness):
    author_repository = AuthorRepository(session)
    await author_repository.update_author_business(author_id, plane_bussyness)


async def db_register_author(session, author_id, card_number, specialities, telegram_url):
    author_repository = AuthorRepository(session)
    specialities = "/".join(list(set(specialities)))
    await author_repository.register_author(author_id, card_number, specialities, telegram_url)


async def load_crm_authors_to_db(authors: List[AuthorSchema]):
    async with session_maker() as session:
        author_repository = AuthorRepository(session)

        for author in authors:
            author = author.model_dump()

            author["specialities"] = "/".join([speciality["name"] for speciality in author["specialities"]])

            author_db = await author_repository.get(id=author["id"])

            if author_db:
                for key, value in author.items():
                    setattr(author_db, key, value)
            else:
                await author_repository.create(author)

        await session.commit()
