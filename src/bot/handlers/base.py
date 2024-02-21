from aiogram import Router, types
from loguru import logger

from src.db.services.admin import get_admin_authors
from src.worker.tasks import test_task

router = Router(name="base")


@router.message()
async def base_test(message: types.Message, session):
    user_id = message.from_user.id
    authors = await get_admin_authors(session, user_id)

    for author in authors:
        logger.info(f"{author.id}, {author.raiting}")

    test_task.apply_async(
        countdown=10,
    )
