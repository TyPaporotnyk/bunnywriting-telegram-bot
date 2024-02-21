from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Author
from src.db.repositories.author import AuthorRepository


async def create_base_author(session: AsyncSession, author_data: dict):
    author_repository = AuthorRepository(session)

    await author_repository.create(author_data)


async def get_author_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[Author]:
    author_repository = AuthorRepository(session)

    author = await author_repository.get(id=telegram_id)
    return author
