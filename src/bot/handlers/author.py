from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from loguru import logger

from src.bot.filters.user import IsAuthor
from src.bot.filters.admin import IsAdmin

from src.db.services.admin import get_admin_authors

router = Router(name="commands")


@router.message(CommandStart(), IsAuthor())
async def author_start(message: types.Message):
    user_id = message.from_user.id

    logger.info("User {user_id} has send message", user_id=user_id)


@router.message(Command(commands="help"), IsAuthor())
async def author_help(message: types.Message):
    user_id = message.from_user.id

    logger.info("User {user_id} has send message", user_id=user_id)
