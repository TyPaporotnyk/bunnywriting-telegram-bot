from typing import Union, Dict, Any

from aiogram import types
from aiogram.filters.base import Filter


class IsAuthor(Filter):
    async def __call__(self, obj: types.Message) -> Union[bool, Dict[str, Any]]:
        return obj.chat.type in ["group", "supergroup"]
