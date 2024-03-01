from typing import Any, Dict, Union

from aiogram import types
from aiogram.filters.base import Filter

from src.db.services.admin import get_admin_ids


class IsAdmin(Filter):
    async def __call__(self, obj: types.Message, session) -> Union[bool, Dict[str, Any]]:
        admin_ids = await get_admin_ids(session)

        return obj.from_user.id in admin_ids
