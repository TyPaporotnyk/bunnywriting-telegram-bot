from typing import Any, Dict, Union

from aiogram import types
from aiogram.filters.base import Filter
from loguru import logger

from src.db.services.admin import get_admin_ids


class IsAdmin(Filter):
    async def __call__(self, obj: types.Message, session) -> Union[bool, Dict[str, Any]]:
        admin_ids = await get_admin_ids(session)
        logger.debug(f"{obj.from_user.id}, {admin_ids}")

        return obj.from_user.id in admin_ids
