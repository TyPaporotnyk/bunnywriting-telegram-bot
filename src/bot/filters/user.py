from typing import Any, Dict, Union

from aiogram import types
from aiogram.filters.base import Filter

from src.db.services.user import get_author_by_telegram_id


class IsAuthor(Filter):
    async def __call__(self, obj: types.Message, session) -> Union[bool, Dict[str, Any]]:
        author = await get_author_by_telegram_id(session, obj.from_user.id)
        return author is not None


