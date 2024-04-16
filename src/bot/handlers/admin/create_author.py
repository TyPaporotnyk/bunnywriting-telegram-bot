from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.admin import IsAdmin
from src.bot.states.admin import UserFormState
from src.crm import Author
from src.crm.exceptions import AuthorNotCreated
from src.db.services.author import create_base_author

router = Router(name="admin_create_author")


@router.callback_query(F.data == "add_author", IsAdmin())
async def add_author(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserFormState.user_data)
    await callback.message.answer(
        "Надішліть дані автора автора в такому форматі\n'(айді-телеграм),(айді),(ім'я) (прізвище),(рейтинг)'"
    )


@router.message(UserFormState.user_data)
async def get_author_name(message: types.Message, state: FSMContext, session):
    admin_id = message.from_user.id

    try:
        telegram_id, author_id, full_name, rating = list(map(str.strip, message.text.split(",")))

        await Author.create_author(telegram_id, author_id, full_name, rating, admin_id)
        await create_base_author(
            session, {"id": telegram_id, "name": full_name, "rating": rating, "admin_id": admin_id}
        )

        await message.answer("✅Автор був доданий")
    except AuthorNotCreated:
        await message.answer("❌Автор не був доданий")
    except Exception as e:
        await message.answer("❌Автор не був доданий")
        logger.error(f"Author has not been created by not raized error: {repr(e)}")

    await state.clear()
