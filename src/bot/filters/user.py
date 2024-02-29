from typing import Any, Dict, Union

from aiogram import types
from aiogram.filters.base import Filter

from src.db.services.author import get_author_by_telegram_id


class IsNotRegisteredAuthor(Filter):
    async def __call__(self, obj: types.Message, session) -> Union[bool, Dict[str, Any]]:
        author = await get_author_by_telegram_id(session, obj.from_user.id)
        if author:
            return author.card_number is None
        else:
            return False


class IsAuthor(Filter):
    async def __call__(self, obj: types.Message, session) -> Union[bool, Dict[str, Any]]:
        author = await get_author_by_telegram_id(session, obj.from_user.id)
        return author is not None
