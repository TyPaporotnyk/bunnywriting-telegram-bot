from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from loguru import logger

from src.db.repositories import AuthorRepository

router = Router(name="commands")


@router.message(CommandStart())
async def test(message: types.Message):
    user_id = message.from_user.id

    logger.info("User {user_id} has send message", user_id=user_id)


@router.message(Command(commands="help"))
async def test(message: types.Message):
    user_id = message.from_user.id

    logger.info("User {user_id} has send message", user_id=user_id)


@router.message(F.text)
async def test(message: types.Message, session):
    author_id = await AuthorRepository(session).get(id=123, full_name="Test")
    logger.info(author_id)
    logger.info(session.in_transaction())